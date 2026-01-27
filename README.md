# xParse Document Parsing Tool

**Author:** intsig-textin  
**Version:** 0.0.1  
**Type:** tool

---

## Description

xParse Document Parsing Tool extracts structured content from various file formats (PDF, WORD, EXCEL, PPT, images, etc.) and converts them into queryable and analyzable structured elements.

---

## Provider Credentials

When configuring the plugin in Dify, you need to provide the following credentials:

> **Get your credentials:** Please [log in to Textin](https://www.textin.com/console/dashboard/setting) and go to **Workspace → Account Settings → Developer Information** to view your `x-ti-app-id` and `x-ti-secret-code`.

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ---------- |
| `x-ti-app-id` | secret-input | Yes | Textin application ID. Please [log in to Textin](https://www.textin.com/console/dashboard/setting) and go to "Workspace → Account Settings → Developer Information" to view x-ti-app-id. See [API Documentation](https://docs.textin.com/api-reference/endpoint/pipeline) for details. |
| `x-ti-secret-code` | secret-input | Yes | Textin secret code. Please [log in to Textin](https://www.textin.com/console/dashboard/setting) and go to "Workspace → Account Settings → Developer Information" to view x-ti-secret-code. See [API Documentation](https://docs.textin.com/api-reference/endpoint/pipeline) for details. |

---

## Parse Input Parameters

The xParse Parse tool provides parameters to customize the processing of documents.

> **The only required parameter is `file`** – the file you wish to process.

---

### Main Parameters

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ---------- |
| `file` | file | **Yes** | - | The file to be parsed (supports PDF, WORD, EXCEL, PPT, images, etc.) |
| `provider` | select | No | `textin` | The document parsing provider/engine to use. Options: `textin` (Recommended), `textin-lite`, `mineru`, `paddle` |
| `pdf_pwd` | string | No | - | Password for encrypted PDF files |
| `page_ranges` | string | No | - | Specify page ranges to parse. Format: `"15"` for page 15, `"20-25"` for pages 20-25, `"1,3,5-7"` for pages 1, 3, 5, 6, 7 |
| `crop_dewarp` | select | No | `0` | Whether to perform crop and dewarp preprocessing. Options: `0` (No), `1` (Yes) |
| `remove_watermark` | select | No | `0` | Whether to remove watermark preprocessing. Options: `0` (No), `1` (Yes) |
| `get_page_image` | boolean | No | `false` | Whether to return page images (for PDF and other formats that need to be converted to images) |
| `get_sub_image` | boolean | No | `false` | Whether to return sub-images within pages |

---

### TextIn Engine Specific Parameters

The following parameters only apply when `provider` is set to `textin`:

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ---------- |
| `parse_mode` | select | No | `scan` | PDF parsing mode. Options: `auto` (extract text directly from PDF), `scan` (treat PDF as images). Note: Images always use scan mode |
| `underline_level` | select | No | `0` | Control underline recognition range (only for scan mode). Options: `0` (No recognition), `1` (Only recognize underlines without text) |
| `apply_chart` | select | No | `0` | Whether to enable chart recognition. Recognized charts will be output as tables. Options: `0` (No), `1` (Yes) |

---

### Advanced Parameters

| Parameter | Type | Required | Default | Description |
| --------- | ---- | -------- | ------- | ---------- |
| `image_storage_config` | string | No | - | JSON format S3 storage configuration for storing page images. Includes: `endpoint`, `access_key`, `secret_key`, `bucket`, `region`, `prefix`, `url_prefix` |

---

## Notes

- For more details on each parameter, refer to the [xParse Parse Documentation](https://docs.textin.com/pipeline/parse).
- Some parameters are only available for specific providers or file types.
- Default values are shown where applicable.

---

## API Response Structure

### Top-Level Fields

The tool returns structured data with the following fields:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `text` | string | The full parsed content in Markdown format, including images, sections, etc. |
| `elements` | array of object | List of structured content blocks (sections, paragraphs, images, tables, etc.) |
| `images` | array of object | List of image objects extracted from the content (if `get_sub_image` or `get_page_image` is enabled) |

---

### Field Details

#### text

- **Type:** string  
- **Description:**  
  The entire content, formatted in Markdown. This includes images (as markdown image syntax), headings, paragraphs, and other formatting for direct rendering.

#### elements

- **Type:** array of objects  
- **Description:**  
  List of structured content blocks. Each object represents a section, paragraph, image, table, or other content element extracted from the document.

Each element object contains:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `element_id` | string | Unique identifier for the element (SHA-256 hash of text + coordinates + page number + filename) |
| `type` | string | The type of element (e.g., `NarrativeText`, `Title`, `Image`, `Table`, `FigureCaption`) |
| `text` | string | The text content of the element |
| `metadata` | object | Metadata for the element (see below for details) |

##### metadata (object)

The `metadata` field provides detailed information about the element's origin, layout, and context.

Common fields include:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `filename` | string | Name of the source file (e.g., `example.pdf`) |
| `filetype` | string | MIME type or file type (e.g., `application/pdf`) |
| `last_modified` | string | Timestamp of last file modification |
| `page_number` | integer | Page number in the source file (if applicable) |
| `page_width` | integer | Width of the page in pixels |
| `page_height` | integer | Height of the page in pixels |
| `coordinates` | array | 8-element array representing quadrilateral coordinates (normalized, range [0, 1]) |
| `parent_id` | string | ID of the parent element |
| `category_depth` | integer | Depth in the document hierarchy |
| `image_base64` | string | Base64 encoded image data (if `get_sub_image` is enabled) |
| `image_mime_type` | string | MIME type for images (e.g., `image/png`) |
| `page_image_url` | string | URL for page image (if `get_page_image` is enabled) |
| `original_image_url` | string | URL for original page image (if preprocessing is enabled) |
| `preview_url` | string | Preview URL for images (after uploading to Dify) |
| `dify_file_id` | string | Unique file ID for images in Dify |
| `text_as_html` | string | HTML representation for tables or rich text elements |
| `data_source` | object | Data source information including record locator, URLs, version, dates |

#### images

- **Type:** array of objects  
- **Description:**  
  List of images found in the content (only returned if `get_sub_image` or `get_page_image` is enabled). Each image object contains:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `id` | string | Unique image ID (Dify file ID) |
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
  "text": "![Document Image](https://dify.example.com/files/tools/a1b2c3d4-5678-90ab-cdef-1234567890ab.png)\n\n# Document Title\n\nThis is a sample document with structured content.\n\n## Section 1\n\nParagraph text here.\n\n## Section 2\n\nMore content...",
  "elements": [
    {
      "element_id": "13a9939f23e485ca20a16c741658bcf64efd82309a6f0a8cf35679a65b2fd0dc",
      "type": "Title",
      "text": "Document Title",
      "metadata": {
        "filename": "example.pdf",
        "filetype": "application/pdf",
        "last_modified": "1758624866230",
        "page_number": 1,
        "page_width": 1191,
        "page_height": 1684,
        "coordinates": [0.1822, 0.2316, 0.6717, 0.2316, 0.6717, 0.2732, 0.1822, 0.2732],
        "parent_id": "23a9939f23e485ca20a16c741658bcf64efd82309a6f0a8cf35679a65b2fd0dc",
        "category_depth": 1,
        "data_source": {
          "record_locator": {
            "protocol": "file",
            "remote_file_path": "/projects/demo/example.pdf"
          },
          "url": "file:///projects/demo/example.pdf",
          "version": "1758624866230967485",
          "date_created": "1764555574237",
          "date_modified": "1758624866230",
          "date_processed": "1764742970688"
        }
      }
    },
    {
      "element_id": "23a9939f23e485ca20a16c741658bcf64efd82309a6f0a8cf35679a65b2fd0dc",
      "type": "NarrativeText",
      "text": "This is a sample document with structured content.",
      "metadata": {
        "filename": "example.pdf",
        "filetype": "application/pdf",
        "last_modified": "1758624866230",
        "page_number": 1,
        "page_width": 1191,
        "page_height": 1684,
        "coordinates": [0.1822, 0.2732, 0.6717, 0.2732, 0.6717, 0.3150, 0.1822, 0.3150],
        "parent_id": "23a9939f23e485ca20a16c741658bcf64efd82309a6f0a8cf35679a65b2fd0dc",
        "category_depth": 1
      }
    },
    {
      "element_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "type": "Image",
      "text": "",
      "metadata": {
        "filename": "example.pdf",
        "filetype": "application/pdf",
        "page_number": 1,
        "dify_file_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
        "image_mime_type": "image/png",
        "preview_url": "https://dify.example.com/files/tools/a1b2c3d4-5678-90ab-cdef-1234567890ab.png"
      }
    }
  ],
  "images": [
    {
      "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "name": "image_a1b2c3d4-5678-90ab-cdef-1234567890ab.png",
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
5. Get parsed structured content and images

---

## API Reference

- [xParse Pipeline API](https://docs.textin.com/api-reference/endpoint/pipeline)
- [xParse Parse Documentation](https://docs.textin.com/pipeline/parse)

---

## Notes

- The `text` field is suitable for direct display in web or app frontends.
- The `elements` field is useful for structured processing, highlighting, or further analysis.
- The `images` field provides all image resources for preview or download.
- The `metadata` object in each element may contain additional fields depending on the extraction process and file type.
- Image processing: When `get_sub_image` or `get_page_image` is enabled, images are automatically uploaded to Dify's file system and their URLs are included in the response.

