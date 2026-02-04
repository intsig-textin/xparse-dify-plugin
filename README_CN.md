# xParse 文档解析工具

**作者：** intsig-textin  
**版本：** 0.0.1  
**类型：** tool

---

## 简介

xParse 文档解析工具可以从多种文件格式（PDF、WORD、EXCEL、PPT、图片等）中提取结构化内容，并将其转换为可查询、可分析的结构化元素。

---

## 提供商凭证

在 Dify 中配置此插件时，需要提供以下凭证：

> **获取凭证：** 请[登录 Textin](https://www.textin.com/console/dashboard/setting)，前往 **工作台 → 账号与开发者信息** 查看您的 `x-ti-app-id` 和 `x-ti-secret-code`。

| 参数 | 类型 | 必填 | 说明 |
| --------- | ---- | -------- | ---------- |
| `x-ti-app-id` | secret-input | 是 | Textin APP ID。请[登录 Textin](https://www.textin.com/console/dashboard/setting)，前往"工作台 → 账号与开发者信息"查看 x-ti-app-id。详情请参阅 [API 文档](https://docs.textin.com/api-reference/endpoint/pipeline)。 |
| `x-ti-secret-code` | secret-input | 是 | Textin 密钥。请[登录 Textin](https://www.textin.com/console/dashboard/setting)，前往"工作台 → 账号与开发者信息"查看 x-ti-secret-code。详情请参阅 [API 文档](https://docs.textin.com/api-reference/endpoint/pipeline)。 |

---

## 解析输入参数

xParse 解析工具提供了用于自定义文档处理的参数。

> **唯一必填参数是 `file`** —— 您要处理的文件。

---

### 主要参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --------- | ---- | -------- | ------- | ---------- |
| `file` | file | **是** | - | 要解析的文件（支持 PDF、WORD、EXCEL、PPT、图片等） |
| `provider` | select | 否 | `textin` | 使用的文档解析提供商/引擎。选项：`textin`（推荐）、`textin-lite`、`mineru`、`paddle` |
| `pdf_pwd` | string | 否 | - | 加密 PDF 文件的密码 |
| `page_ranges` | string | 否 | - | 指定要解析的页面范围。格式：`"15"` 表示第 15 页，`"20-25"` 表示第 20-25 页，`"1,3,5-7"` 表示第 1、3、5、6、7 页 |
| `crop_dewarp` | select | 否 | `0` | 是否执行裁剪和去扭曲预处理。选项：`0`（否）、`1`（是） |
| `remove_watermark` | select | 否 | `0` | 是否移除水印预处理。选项：`0`（否）、`1`（是） |
| `get_page_image` | boolean | 否 | `false` | 是否返回页面图片（适用于 PDF 等需要转换为图片的格式） |
| `get_sub_image` | boolean | 否 | `false` | 是否返回页面内的子图片 |

---

### TextIn 引擎专用参数

以下参数仅在 `provider` 设置为 `textin` 时生效：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --------- | ---- | -------- | ------- | ---------- |
| `parse_mode` | select | 否 | `scan` | PDF 解析模式。选项：`auto`（直接从 PDF 提取文本）、`scan`（将 PDF 视为图片处理）。注意：图片始终使用 scan 模式 |
| `underline_level` | select | 否 | `0` | 控制下划线识别范围（仅适用于 scan 模式）。选项：`0`（不识别）、`1`（仅识别无文字的下划线） |
| `apply_chart` | select | 否 | `0` | 是否启用图表识别。识别到的图表将输出为表格。选项：`0`（否）、`1`（是） |

---

### 高级参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --------- | ---- | -------- | ------- | ---------- |
| `image_storage_config` | string | 否 | - | JSON 格式的 S3 存储配置，用于存储页面图片。包括：`endpoint`、`access_key`、`secret_key`、`bucket`、`region`、`prefix`、`url_prefix` |

---

## 注意事项

- 有关各参数的更多详情，请参阅 [xParse 解析文档](https://docs.textin.com/pipeline/parse)。
- 某些参数仅适用于特定的提供商或文件类型。
- 适用情况下会显示默认值。

---

## API 响应结构

### 顶级字段

工具返回包含以下字段的结构化数据：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `text` | string | 完整的解析内容（Markdown 格式），包括图片、章节等 |
| `elements` | array of object | 结构化内容块列表（章节、段落、图片、表格等） |
| `images` | array of object | 从内容中提取的图片对象列表（如果启用了 `get_sub_image` 或 `get_page_image`） |

---

### 字段详情

#### text

- **类型：** string  
- **说明：**  
  完整内容，以 Markdown 格式呈现。包括图片（以 markdown 图片语法表示）、标题、段落和其他格式，可直接渲染。

#### elements

- **类型：** array of objects  
- **说明：**  
  结构化内容块列表。每个对象代表从文档中提取的一个章节、段落、图片、表格或其他内容元素。

每个元素对象包含：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `element_id` | string | 元素的唯一标识符（文本 + 坐标 + 页码 + 文件名的 SHA-256 哈希值） |
| `type` | string | 元素类型（例如：`NarrativeText`、`Title`、`Image`、`Table`、`FigureCaption`） |
| `text` | string | 元素的文本内容 |
| `metadata` | object | 元素的元数据（详见下文） |

##### metadata (object)

`metadata` 字段提供有关元素来源、布局和上下文的详细信息。

常见字段包括：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `filename` | string | 源文件名（例如：`example.pdf`） |
| `filetype` | string | MIME 类型或文件类型（例如：`application/pdf`） |
| `last_modified` | string | 文件最后修改时间戳 |
| `page_number` | integer | 源文件中的页码（如适用） |
| `page_width` | integer | 页面宽度（像素） |
| `page_height` | integer | 页面高度（像素） |
| `coordinates` | array | 8 元素数组，表示四边形坐标（归一化，范围 [0, 1]） |
| `parent_id` | string | 父元素的 ID |
| `category_depth` | integer | 文档层次结构中的深度 |
| `image_base64` | string | Base64 编码的图片数据（如果启用了 `get_sub_image`） |
| `image_mime_type` | string | 图片的 MIME 类型（例如：`image/png`） |
| `page_image_url` | string | 页面图片的 URL（如果启用了 `get_page_image`） |
| `original_image_url` | string | 原始页面图片的 URL（如果启用了预处理） |
| `preview_url` | string | 图片的预览 URL（上传到 Dify 后） |
| `dify_file_id` | string | Dify 中图片的唯一文件 ID |
| `text_as_html` | string | 表格或富文本元素的 HTML 表示 |
| `data_source` | object | 数据源信息，包括记录文件位置、URL、版本、日期 |

#### images

- **类型：** array of objects  
- **说明：**  
  内容中找到的图片列表（仅在启用 `get_sub_image` 或 `get_page_image` 时返回）。每个图片对象包含：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `id` | string | 唯一图片 ID（Dify 文件 ID） |
| `name` | string | 图片文件名 |
| `mime_type` | string | 图片的 MIME 类型 |
| `preview_url` | string | 图片预览 URL |
| `size` | integer | 图片文件大小（字节） |
| `type` | string | 始终为 `"image"` |

---

## 响应示例

### JSON 结构

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

## 使用方法

1. 在 Dify 中安装此插件
2. 配置提供商凭证（`x-ti-app-id` 和 `x-ti-secret-code`）
3. 在工作流或智能体应用中使用解析工具
4. 上传文件并配置解析参数
5. 获取解析后的结构化内容和图片

---

## API 参考

- [xParse Pipeline API](https://docs.textin.com/api-reference/endpoint/pipeline)
- [xParse 解析文档](https://docs.textin.com/pipeline/parse)

---

## 注意事项

- `text` 字段适合在 Web 或应用前端直接显示。
- `elements` 字段适用于结构化处理、高亮显示或进一步分析。
- `images` 字段提供所有图片资源，可用于预览或下载。
- 每个元素中的 `metadata` 对象可能包含其他字段，具体取决于提取过程和文件类型。
- 图片处理：
  - 当启用 `get_sub_image` 时，图片（`image_base64`）会自动解码并上传到 Dify 的文件系统，其 `preview_url` 和 `dify_file_id` 会包含在响应的 `metadata` 中，同时图片会被添加到 `images` 列表中。
  - 当启用 `get_page_image` 时，页面图片的 URL（`page_image_url`）会直接包含在响应的 `metadata` 中，不会上传到 Dify 文件系统。
