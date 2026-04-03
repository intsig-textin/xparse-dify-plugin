# xParse Document Parsing Tool

**Author:** intsig-textin  
**Version:** 1.2.0  
**Type:** tool

---

## Description

xParse Document Parsing Tool extracts structured content from various file formats (PDF, WORD, EXCEL, PPT, images, etc.) and converts them into AI-friendly structured data with rich metadata.

---

## Provider Credentials

When configuring the plugin in Dify, you need to provide the following credentials:

> **Get your credentials:** Please [log in to Textin](https://www.textin.com/console/dashboard/setting) and go to **Workspace → Account Settings → Developer Information** to view your `x-ti-app-id` and `x-ti-secret-code`.

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ---------- |
| `x-ti-app-id` | secret-input | Yes | Textin application ID. Please [log in to Textin](https://www.textin.com/console/dashboard/setting) and go to "Workspace → Account Settings → Developer Information" to view x-ti-app-id. See [API Documentation](https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync) for details. |
| `x-ti-secret-code` | secret-input | Yes | Textin secret code. Please [log in to Textin](https://www.textin.com/console/dashboard/setting) and go to "Workspace → Account Settings → Developer Information" to view x-ti-secret-code. See [API Documentation](https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync) for details. |

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

## Usage

1. Install this plugin in Dify
2. Configure Provider credentials (`x-ti-app-id` and `x-ti-secret-code`)
3. Use the Parse tool in Workflow or Agent applications
4. Upload a file and configure parsing parameters
5. Get structured content including markdown, elements, and optional pages/title_tree/images

---

## API Reference

- [Parse Sync API](https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync)
- [Parse Config Documentation](https://docs.textin.com/xparse/v1/parse-config)
- [Parse Response Documentation](https://docs.textin.com/xparse/v1/parse-response)

---

## Breaking Changes in v1.2.0

This version migrates from the legacy Pipeline API to the new Parse Sync API (v1.3.0). Key changes:

**Removed Parameters:**
- `provider` - no longer exposed (always uses textin engine)
- `crop_dewarp` - not available in new API
- `remove_watermark` - not available in new API
- `get_page_image` - replaced by `pages` capability
- `get_sub_image` - replaced by `include_image_data` capability
- `parse_mode` - not available in new API
- `underline_level` - not available in new API
- `apply_chart` - not available in new API
- `image_storage_config` - not available in new API

**New Parameters:**
- `include_hierarchy` (boolean) - control element relationship data
- `include_inline_objects` (boolean) - extract formulas, handwriting, etc.
- `include_char_details` (boolean) - character-level recognition details
- `include_image_data` (boolean) - image data with auto-upload to Dify
- `include_table_structure` (boolean) - detailed table structure
- `pages` (boolean) - page metadata list
- `title_tree` (boolean) - document outline
- `table_view` (select) - table format in markdown

**Output Changes:**
- `text` now comes directly from API's `markdown` field
- `elements` structure updated to match new API schema
- New output variables: `pages`, `title_tree`
- `images` only returned when `include_image_data` is enabled

---

## Notes

- The `text` field contains the full Markdown representation suitable for direct display.
- The `elements` field provides structured data for advanced processing and analysis.
- The `pages` and `title_tree` fields offer document structure insights.
- When `include_image_data` is enabled, images with base64 data are automatically uploaded to Dify's file system, and the `images` array contains the uploaded file information.
- Coordinates are normalized to [0, 1] range relative to page dimensions. To convert to pixels, multiply by page width/height.
