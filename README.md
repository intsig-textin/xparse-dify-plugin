# xParse for RAG and Agents

**Author:** intsig-textin  
**Version:** 1.2.1
**Type:** tool

---

## Description

Parse complex documents into Markdown, structured elements, tables, and images for RAG pipelines and agent workflows.

xParse is a structured document parsing tool built for RAG pipelines and agent workflows. It parses PDFs, Word, Excel, PowerPoint, images, and other files into model-ready outputs, including Markdown text, structured elements, tables, and images.

Unlike simple document-to-text conversion tools, xParse is designed for workflows that need richer document structure and layout-aware understanding. It helps turn complex files into content that can be used for knowledge ingestion, retrieval, agent reasoning, information extraction, and downstream automation.

Use xParse when your workflow needs more than plain text output — for example, when you need document sections, titles, tables, image blocks, page-level metadata, or structured content elements that can be passed into later nodes in Dify. xParse returns Markdown in the `text` field, structured blocks in `elements`, and image resources in `images`, which makes it more suitable for multi-step workflows than a simple Markdown-only parser.

**Supports both Free API and Paid API** — install and use immediately without any credentials.

---

## Best For

- RAG document preprocessing
- Knowledge base ingestion
- Agent document reading and reasoning
- Structured information extraction
- Table and layout-aware parsing
- Multi-step workflow automation
- Image-aware document understanding

---

## Quick Start

### 1. Free API (Default, No Credentials Required)

Simply install the plugin in Dify and start using it — **no credentials needed**. Leave the `x-ti-app-id` and `x-ti-secret-code` fields empty during provider configuration.

The free API supports PDF and images (JPG/PNG/BMP/TIFF/WebP), with a daily limit of 1,000 pages.

### 2. Paid API (Optional)

For higher usage or more formats (Word/Excel/PPT/HTML/OFD and 20+ other formats), get credentials from [Textin Console](https://www.textin.com/user/login?redirect=%252Fconsole%252Fdashboard%252Fsetting&from=xparse-dify-plugin) and fill in `x-ti-app-id` and `x-ti-secret-code` in the provider configuration.

---

## Provider Credentials

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ---------- |
| `x-ti-app-id` | secret-input | No | Textin application ID. Only required for paid API. Leave empty to use the free API. |
| `x-ti-secret-code` | secret-input | No | Textin secret code. Only required for paid API. Leave empty to use the free API. |

> **Get credentials for paid API:** Please [login to Textin](https://www.textin.com/console/dashboard/setting) and go to **Workspace → Account Settings → Developer Information** to view your `x-ti-app-id` and `x-ti-secret-code`.

---

## Parse Input Parameters

The xParse Parse tool provides parameters to customize document processing and control the level of detail in returned data.

> **The only required parameter is `file`** – the file you wish to process.

---

### Main Parameters

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ---------- |
| `file` | file | **Yes** | - | The file to be parsed (supports PDF, WORD, EXCEL, PPT, images, etc.) |
| `pdf_pwd` | string | No | - | Password for encrypted PDF files |
| `page_ranges` | string | No | - | Specify page ranges to parse. Format: `"1-2"` for pages 1-2, `"1-2,3-4,5-10"` for multiple ranges |

---

### Capabilities Parameters

Control what additional information is included in the response:

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ---------- |
| `include_hierarchy` | boolean | No | `true` | Whether to return element hierarchy and relationships (parent_id, children_ids, ref_element_id) for building document structure graph |
| `include_inline_objects` | boolean | No | `false` | Whether to return fine-grained inline objects (formulas, handwriting, checkboxes, images within text) |
| `include_char_details` | boolean | No | `false` | Whether to return character-level details (coordinates, confidence, candidate characters) |
| `include_image_data` | boolean | No | `false` | Whether to return image data (image_url, mime_type, base64). When enabled, base64 images are automatically uploaded to Dify |
| `include_table_structure` | boolean | No | `false` | Whether to return detailed table structure in JSON format (rows, cols, cells with coordinates and content) |
| `pages` | boolean | No | `false` | Whether to return page metadata list (page dimensions, page_image_url, element_ids per page) |
| `title_tree` | boolean | No | `false` | Whether to return hierarchical title tree (table of contents) |
| `table_view` | select | No | `html` | Format of tables in markdown. Options: `markdown` (simple), `html` (supports complex tables with merged cells) |

---

## API Limits

| Limit | Free API | Paid API |
|-------|----------|----------|
| Supported formats | PDF, images (JPG/PNG/BMP/TIFF/WebP) | 20+ formats (PDF, images, Word, Excel, PPT, HTML, OFD, etc.) |
| Daily usage | 1,000 pages | Per plan |
| File size | 10MB | 500MB |
| PDF pages | — | 1,000 pages |
| XLS/XLSX/CSV | — | ≤ 2,000 rows × 100 cols per sheet |
| TXT | — | ≤ 100KB |
| Image dimensions | 20–20,000 px | 20–20,000 px |

---

## Notes

- For more details on capabilities and parameters, refer to the [Parse Config Documentation](https://docs.textin.com/xparse/v1/parse-config).
- Enable only the capabilities you need to optimize performance and response size.
- Default values are optimized for common use cases.

---

## API Response Structure

### Top-Level Output Variables

The tool returns structured data with the following output variables:

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `text` | string | The full document content in Markdown format (from API's `markdown` field) |
| `elements` | array of object | List of structured elements extracted from the document |
| `pages` | array of object | List of page metadata (only returned if `pages` capability is enabled) |
| `title_tree` | array of object | Hierarchical title tree / table of contents (only returned if `title_tree` capability is enabled) |
| `images` | array of object | List of images uploaded to Dify (only returned if `include_image_data` is enabled and images are present) |

---

### Field Details

#### text

- **Type:** string  
- **Description:**  
  The entire document content formatted in Markdown. This comes directly from the API's `markdown` field and includes proper formatting for headings, paragraphs, tables, images, etc.

#### elements

- **Type:** array of objects  
- **Description:**  
  List of structured elements extracted from the document. Each element represents a semantic unit (title, paragraph, table, image, etc.) with metadata.

Each element object contains:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `element_id` | string | Unique identifier for the element |
| `type` | string | Element type: `Title`, `NarrativeText`, `ListItem`, `Table`, `Image`, `Formula`, `Header`, `Footer`, `PageNumber`, `FigureCaption`, `TableCaption`, `PageBreak`, `CodeSnippet`, `UncategorizedText` |
| `sub_type` | string | Optional sub-type for further classification (e.g., for Image: `stamp`, `qrcode`, `barcode`, `chart`) |
| `text` | string | Text content of the element |
| `page_number` | integer | Page number where the element appears (starting from 1) |
| `coordinates` | array | 8-element array representing normalized quadrilateral coordinates [x1,y1,x2,y2,x3,y3,x4,y4] in range [0,1] |
| `metadata` | object | Element metadata (see below) |
| `objects` | array | Inline objects within the element (only if `include_inline_objects` is enabled) |
| `table_structure` | object | Table structure details (only for Table elements if `include_table_structure` is enabled) |
| `char_details` | array | Character-level details (only if `include_char_details` is enabled) |
| `image_data` | object | Image data (only for Image elements if `include_image_data` is enabled) |

##### Element metadata

The `metadata` field provides contextual information:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `parent_id` | string | Parent element ID (if `include_hierarchy` is enabled) |
| `children_ids` | array | Child element IDs (if `include_hierarchy` is enabled) |
| `category_depth` | integer | Nesting depth for elements of the same type (e.g., 0 for H1, 1 for H2) |
| `ref_element_id` | string | Referenced element ID, e.g., linking image to its caption (if `include_hierarchy` is enabled) |
| `is_continuation` | boolean | Whether this element continues from a previous page |
| `continuation_of` | string | Element ID that this continues from (if `is_continuation` is true) |
| `has_inline_objects` | boolean | Whether the element contains inline objects |
| `inline_object_types` | array | Types of inline objects present (e.g., `["formula", "handwriting"]`) |
| `width` | integer | Image width in pixels (for Image elements) |
| `height` | integer | Image height in pixels (for Image elements) |
| `data_source` | object | Data source information including protocol, path, and URLs |

#### pages

- **Type:** array of objects  
- **Description:**  
  List of page metadata (only returned if `pages` capability is enabled). Each page object contains:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `page_number` | integer | Page number (starting from 1) |
| `page_width` | number | Page width in pixels |
| `page_height` | number | Page height in pixels |
| `page_image_url` | string | URL of the rendered page image |
| `element_ids` | array | List of element IDs on this page in reading order |
| `dpi` | integer | DPI used for rendering |
| `angle` | number | Page rotation angle (0 is normal reading orientation, clockwise) |
| `status` | string | Processing status of the page |

#### title_tree

- **Type:** array of objects  
- **Description:**  
  Hierarchical document outline (only returned if `title_tree` capability is enabled). Each node contains:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `element_id` | string | Element ID of the corresponding Title element |
| `title` | string | Title text |
| `level` | integer | Title level (1 is highest, i.e., H1) |
| `page_number` | integer | Page number where the title appears |
| `children` | array | Nested child title nodes |

#### images

- **Type:** array of objects  
- **Description:**  
  List of images uploaded to Dify's file system (only returned if `include_image_data` is enabled and images with base64 data are present). Each image object contains:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | string | Dify file ID |
| `name` | string | Image file name |
| `mime_type` | string | MIME type of the image |
| `preview_url` | string | URL for image preview |
| `size` | integer | Image file size in bytes |
| `type` | string | Always `"image"` |

---

## Example Response

### JSON Structure

```json
{
  "text": "# Document Title\n\nThis is the document content in Markdown format...\n\n## Section 1\n\nParagraph text here.\n\n<table>\n  <tr><th>Column 1</th><th>Column 2</th></tr>\n  <tr><td>Data 1</td><td>Data 2</td></tr>\n</table>",
  "elements": [
    {
      "element_id": "el_001",
      "type": "Title",
      "text": "Document Title",
      "page_number": 1,
      "coordinates": [0.1822, 0.2316, 0.6717, 0.2316, 0.6717, 0.2732, 0.1822, 0.2732],
      "metadata": {
        "category_depth": 0,
        "children_ids": ["el_002", "el_003"],
        "data_source": {
          "record_locator": {
            "protocol": "file",
            "remote_file_path": "/projects/demo/document.pdf"
          },
          "url": "file:///projects/demo/document.pdf"
        }
      }
    },
    {
      "element_id": "el_002",
      "type": "NarrativeText",
      "text": "This is the document content in Markdown format...",
      "page_number": 1,
      "coordinates": [0.1822, 0.2732, 0.6717, 0.2732, 0.6717, 0.3150, 0.1822, 0.3150],
      "metadata": {
        "parent_id": "el_001"
      }
    }
  ],
  "pages": [
    {
      "page_number": 1,
      "page_width": 1576,
      "page_height": 1683,
      "page_image_url": "https://example.com/page-1.jpg",
      "element_ids": ["el_001", "el_002", "el_003"],
      "dpi": 144,
      "angle": 0,
      "status": "Success"
    }
  ],
  "title_tree": [
    {
      "element_id": "el_001",
      "title": "Document Title",
      "level": 1,
      "page_number": 1,
      "children": [
        {
          "element_id": "el_003",
          "title": "Section 1",
          "level": 2,
          "page_number": 1,
          "children": []
        }
      ]
    }
  ],
  "images": [
    {
      "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "name": "image_el_010.png",
      "mime_type": "image/png",
      "preview_url": "https://dify.example.com/files/tools/a1b2c3d4-5678-90ab-cdef-1234567890ab.png",
      "size": 20480,
      "type": "image"
    }
  ]
}
```

---

## Typical Workflow Use Cases

1. **Knowledge ingestion for RAG** — Upload a PDF or Office file → parse into Markdown and structured elements → chunk and index into your knowledge base.
2. **Agent document understanding** — Let your agent read contracts, reports, manuals, and forms through structured outputs instead of raw files.
3. **Structured information extraction** — Parse documents first, then pass clean text blocks, tables, and metadata into downstream extraction, summarization, or decision nodes.
4. **Layout-aware processing** — Use titles, page coordinates, tables, and image blocks to support more accurate retrieval, routing, and document automation.

---

## Usage

1. Install this plugin in Dify
2. Configure Provider — leave credentials empty for free API, or fill in for paid API
3. Use the Parse tool in Workflow or Agent applications
4. Upload a file and configure parsing parameters
5. Use the returned `text`, `elements`, and `images` in downstream nodes

---

## API Reference

- [Parse Sync API](https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync)
- [Parse Config Documentation](https://docs.textin.com/xparse/v1/parse-config)
- [Parse Response Documentation](https://docs.textin.com/xparse/v1/parse-response)

---

## Notes

- The `text` field is suitable for direct display or LLM input.
- The `elements` field is useful for structured processing, chunking, highlighting, and further analysis.
- The `images` field provides image resources for preview or multimodal workflows.
- The `pages` and `title_tree` fields offer document structure insights.
- When `include_image_data` is enabled, images with base64 data are automatically uploaded to Dify's file system, and the `images` array contains the uploaded file information.
- Coordinates are normalized to [0, 1] range relative to page dimensions. To convert to pixels, multiply by page width/height.

---

Tags: RAG, Agent, Document Parsing, Structured Extraction, Knowledge Ingestion, PDF Parsing, Markdown, Tables, Layout Parsing
