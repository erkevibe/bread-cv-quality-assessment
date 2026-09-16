#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  ExternalHyperlink,
  Footer,
  Header,
  HeadingLevel,
  ImageRun,
  LevelFormat,
  Packer,
  PageNumber,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableRow,
  TextRun,
  VerticalAlign,
  WidthType,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const PAPER = path.join(ROOT, "paper");
const CONTENT_WIDTH = 10206;
const COLORS = {
  navy: "17365D",
  blue: "2F5597",
  paleBlue: "D9EAF7",
  paleGray: "F2F2F2",
  gray: "666666",
  border: "B7C9D6",
};

function parseCsv(filePath) {
  const [header, ...lines] = fs.readFileSync(filePath, "utf8").trim().split(/\r?\n/);
  const columns = header.split(",");
  return lines.map((line) => {
    const values = line.split(",");
    return Object.fromEntries(columns.map((column, index) => [column, values[index]]));
  });
}

function metric(rows, method, target, name) {
  const row = rows.find(
    (item) =>
      item.method === method &&
      item.split === "test" &&
      item.target === target &&
      item.metric === name,
  );
  if (!row) throw new Error(`Missing metric ${method}/${target}/${name}`);
  return Number(row.value);
}

function stripMarkdown(text) {
  return text
    .replace(/\[([^\]]+)\]\((https?:\/\/.*)\)/g, "$1 — $2")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1");
}

function inlineRuns(text, options = {}) {
  const cleaned = text.replace(/\[([^\]]+)\]\((https?:\/\/.*)\)/g, "$1 — $2");
  const parts = cleaned.split(/(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g).filter(Boolean);
  return parts.map((part) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return new TextRun({ text: part.slice(2, -2), bold: true, ...options });
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return new TextRun({ text: part.slice(1, -1), font: "Courier New", ...options });
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return new TextRun({ text: part.slice(1, -1), italics: true, ...options });
    }
    return new TextRun({ text: part, ...options });
  });
}

function referenceRuns(text) {
  const match = text.match(/^(.*)\[([^\]]+)\]\((https:\/\/.+)\)\.$/);
  if (!match) return inlineRuns(text, { size: 18 });
  return [
    ...inlineRuns(match[1], { size: 18 }),
    new ExternalHyperlink({
      link: match[3],
      children: [new TextRun({ text: match[2], style: "Hyperlink", size: 18 })],
    }),
    new TextRun({ text: ".", size: 18 }),
  ];
}

function pngDimensions(filePath, maxWidth = 620, maxHeight = 390) {
  const data = fs.readFileSync(filePath);
  if (data.toString("ascii", 1, 4) !== "PNG") throw new Error(`Not a PNG: ${filePath}`);
  const width = data.readUInt32BE(16);
  const height = data.readUInt32BE(20);
  const scale = Math.min(maxWidth / width, maxHeight / height);
  return { width: Math.round(width * scale), height: Math.round(height * scale) };
}

function figureParagraph(relativePath, altText) {
  const filePath = path.join(PAPER, relativePath);
  const dimensions = pngDimensions(filePath);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: true,
    spacing: { before: 120, after: 60 },
    children: [
      new ImageRun({
        type: "png",
        data: fs.readFileSync(filePath),
        transformation: dimensions,
        altText: { title: altText, description: altText, name: path.basename(relativePath) },
      }),
    ],
  });
}

const border = { style: BorderStyle.SINGLE, size: 2, color: COLORS.border };
const borders = { top: border, bottom: border, left: border, right: border };

function cell(text, width, options = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders,
    margins: { top: 90, bottom: 90, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    shading: options.header
      ? { fill: COLORS.paleBlue, type: ShadingType.CLEAR }
      : { fill: "FFFFFF", type: ShadingType.CLEAR },
    children: [
      new Paragraph({
        alignment: options.numeric ? AlignmentType.CENTER : AlignmentType.LEFT,
        children: [new TextRun({ text, bold: Boolean(options.header), size: 20 })],
      }),
    ],
  });
}

function makeTable(headers, rows, widths) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((header, index) => cell(header, widths[index], { header: true })),
      }),
      ...rows.map(
        (row) =>
          new TableRow({
            children: row.map((value, index) =>
              cell(String(value), widths[index], { numeric: index > 0 }),
            ),
          }),
      ),
    ],
  });
}

function datasetTable(language, provenance) {
  const ru = language === "ru";
  const counts = provenance.split_counts;
  return makeTable(
    ru ? ["Показатель", "Значение"] : ["Quantity", "Value"],
    [
      [ru ? "Изображений в архиве" : "Archive images", provenance.audit.image_count],
      [ru ? "Строк измерений" : "Measurement rows", provenance.csv_rows],
      [ru ? "Допустимых образцов" : "Eligible samples", provenance.eligible_samples],
      [
        ru ? "Train / validation / test" : "Train / validation / test",
        `${counts.train} / ${counts.validation} / ${counts.test}`,
      ],
      [ru ? "Ошибок сегментации" : "Segmentation failures", provenance.segmentation_failures],
    ],
    [7200, 3006],
  );
}

function resultsTable(language, rows, best) {
  const ru = language === "ru";
  return makeTable(
    ru ? ["Цель", "MAE", "RMSE", "R²"] : ["Target", "MAE", "RMSE", "R²"],
    [
      [
        ru ? "Ширина" : "Width",
        metric(rows, best, "width", "mae").toFixed(3),
        metric(rows, best, "width", "rmse").toFixed(3),
        metric(rows, best, "width", "r2").toFixed(3),
      ],
      [
        ru ? "Высота" : "Height",
        metric(rows, best, "height", "mae").toFixed(3),
        metric(rows, best, "height", "rmse").toFixed(3),
        metric(rows, best, "height", "r2").toFixed(3),
      ],
    ],
    [3000, 2402, 2402, 2402],
  );
}

function parseBlocks(markdown) {
  const lines = markdown.split(/\r?\n/);
  const blocks = [];
  let paragraph = [];
  const flush = () => {
    if (paragraph.length) {
      blocks.push({ type: "paragraph", text: paragraph.join(" ") });
      paragraph = [];
    }
  };
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flush();
    } else if (/^#{1,3} /.test(trimmed)) {
      flush();
      const match = trimmed.match(/^(#{1,3}) (.+)$/);
      blocks.push({ type: "heading", level: match[1].length, text: match[2] });
    } else if (/^!\[.*\]\(.*\)$/.test(trimmed)) {
      flush();
      const match = trimmed.match(/^!\[(.*)\]\((.*)\)$/);
      blocks.push({ type: "image", alt: match[1], path: match[2] });
    } else if (/^\d+\. /.test(trimmed)) {
      flush();
      blocks.push({ type: "reference", text: trimmed.replace(/^\d+\. /, "") });
    } else {
      paragraph.push(trimmed);
    }
  }
  flush();
  return blocks;
}

function makeDocument(inputName, outputName, language, rows, provenance) {
  const markdown = fs.readFileSync(path.join(PAPER, inputName), "utf8");
  const blocks = parseBlocks(markdown);
  const best = provenance.best_method_selected_on_validation;
  const children = [];
  let datasetInserted = false;
  let resultsInserted = false;

  for (const block of blocks) {
    if (block.type === "heading") {
      if (block.level === 1) {
        children.push(
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 0, after: 280 },
            children: [
              new TextRun({ text: stripMarkdown(block.text), bold: true, size: 34, color: COLORS.navy }),
            ],
          }),
        );
      } else {
        const literature = /^(Литература|References)$/.test(block.text);
        children.push(
          new Paragraph({
            heading: block.level === 2 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
            // The Russian article benefits from a dedicated bibliography page.
            // The slightly longer English conclusion otherwise leaves an orphan
            // fragment on a nearly empty page before the references.
            pageBreakBefore: literature && language === "ru",
            keepNext: true,
            children: [new TextRun(stripMarkdown(block.text))],
          }),
        );
        if (/^(2\.1 Набор данных|2\.1 Dataset and audit)$/.test(block.text) && !datasetInserted) {
          children.push(datasetTable(language, provenance));
          datasetInserted = true;
        }
        if (/^3\. /.test(block.text) && !resultsInserted) {
          children.push(resultsTable(language, rows, best));
          resultsInserted = true;
        }
      }
    } else if (block.type === "image") {
      children.push(figureParagraph(block.path, block.alt));
    } else if (block.type === "reference") {
      children.push(
        new Paragraph({
          numbering: { reference: "references", level: 0 },
          alignment: AlignmentType.JUSTIFIED,
          spacing: { after: 90, line: 240 },
          children: referenceRuns(block.text),
        }),
      );
    } else {
      const caption = /^\*\*(Figure|Рисунок) \d+\./.test(block.text);
      const keywords = /^\*\*(Keywords|Ключевые слова):\*\*/.test(block.text);
      children.push(
        new Paragraph({
          alignment: caption ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
          keepNext: keywords,
          spacing: caption ? { after: 180, line: 240 } : { after: 120, line: 276 },
          children: inlineRuns(block.text, {
            size: caption ? 18 : 22,
            italics: caption,
          }),
        }),
      );
    }
  }

  const shortTitle =
    language === "ru"
      ? "Бесконтактная оценка размеров хлеба по RGB-изображениям"
      : "Non-contact bread measurement from RGB images";
  const doc = new Document({
    creator: "Bread CV Quality Assessment project",
    title: stripMarkdown(blocks.find((block) => block.type === "heading").text),
    subject: "Reproducible computer-vision assessment of bread size and shape",
    keywords: "computer vision, bread quality, measurement, machine learning",
    styles: {
      default: {
        document: { run: { font: "Arial", size: 22, color: "000000" } },
      },
      paragraphStyles: [
        {
          id: "Heading1",
          name: "Heading 1",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: "Arial", size: 28, bold: true, color: COLORS.navy },
          paragraph: { spacing: { before: 260, after: 140 }, outlineLevel: 0 },
        },
        {
          id: "Heading2",
          name: "Heading 2",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: "Arial", size: 24, bold: true, color: COLORS.blue },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: "references",
          levels: [
            {
              level: 0,
              format: LevelFormat.DECIMAL,
              text: "%1.",
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 480, hanging: 360 } } },
            },
          ],
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 850, right: 850, bottom: 850, left: 850, header: 425, footer: 425 },
          },
        },
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                border: { bottom: { style: BorderStyle.SINGLE, size: 5, color: COLORS.blue } },
                children: [new TextRun({ text: shortTitle, size: 17, color: COLORS.gray })],
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: language === "ru" ? "Страница " : "Page ", size: 18 }),
                  new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
                ],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });
  return Packer.toBuffer(doc).then((buffer) => {
    const outputPath = path.join(PAPER, outputName);
    fs.writeFileSync(outputPath, buffer);
    console.log(`${outputName}: ${buffer.length} bytes`);
  });
}

async function main() {
  const rows = parseCsv(path.join(ROOT, "results", "metrics", "metrics.csv"));
  const provenance = JSON.parse(
    fs.readFileSync(path.join(ROOT, "results", "metrics", "provenance.json"), "utf8"),
  );
  await makeDocument("article_ru.md", "article_ru.docx", "ru", rows, provenance);
  await makeDocument("article_en.md", "article_en.docx", "en", rows, provenance);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
