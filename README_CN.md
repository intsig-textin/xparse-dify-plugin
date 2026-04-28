# xParse —— 面向 RAG 和 Agent 的智能文档解析

**作者：** intsig-textin  
**版本：** 1.2.1
**类型：** tool

---

## 简介

将复杂文档解析为 Markdown、结构化元素、表格和图片，服务于 RAG 管线和 Agent 工作流。

xParse 是一款面向 RAG 管线和 Agent 工作流的结构化文档解析服务。它可将 PDF、Word、Excel、PowerPoint、图片等文件解析为模型可用的输出，包括 Markdown 文本、结构化元素、表格和图片。

与简单的文档转文本工具不同，xParse 专为需要更丰富文档结构和版面感知理解的工作流设计。它帮助将复杂文件转化为可用于知识入库、检索、Agent 推理、信息抽取和下游自动化的内容。

当你的工作流需要的不仅是纯文本输出时，请使用 xParse —— 例如，当你需要文档章节、标题、表格、图片块、页面级元数据，或可以传递给 Dify 后续节点的结构化内容元素时。xParse 在 `text` 字段返回 Markdown，在 `elements` 中返回结构化块，在 `images` 中返回图片资源，比简单的纯 Markdown 解析器更适合多步骤工作流。

**同时支持免费 API 和付费 API** — 安装后即可直接使用，无需任何凭证。

---

## 适用场景

- RAG 文档预处理
- 知识库数据入库
- Agent 文档阅读与推理
- 结构化信息抽取
- 表格与版面感知解析
- 多步骤工作流自动化
- 图片感知的文档理解

---

## 快速开始

### 1. 免费 API（默认，无需凭证）

只需在 Dify 中安装插件即可直接使用 — **无需任何凭证**。配置提供商时将 `x-ti-app-id` 和 `x-ti-secret-code` 留空即可。

免费 API 支持 PDF 和图片（JPG/PNG/BMP/TIFF/WebP），每日上限 1000 页。

### 2. 付费 API（可选）

如需更多用量或更多格式（Word/Excel/PPT/HTML/OFD 等 20+ 常见格式），请前往 [Textin 控制台](https://www.textin.com/user/login?redirect=%252Fconsole%252Fdashboard%252Fsetting&from=xparse-dify-plugin)获取凭证，并在提供商配置中填入 `x-ti-app-id` 和 `x-ti-secret-code`。

---

## 提供商凭证

| 参数 | 类型 | 必填 | 说明 |
| --------- | ---- | -------- | ---------- |
| `x-ti-app-id` | secret-input | 否 | Textin 应用 ID。仅付费 API 需要，留空则使用免费 API。 |
| `x-ti-secret-code` | secret-input | 否 | Textin 密钥。仅付费 API 需要，留空则使用免费 API。 |

> **获取付费 API 凭证：** 请[登录 Textin](https://www.textin.com/console/dashboard/setting)，前往 **工作台 → 账号设置 → 开发者信息** 查看您的 `x-ti-app-id` 和 `x-ti-secret-code`。

---

## 解析输入参数

xParse 解析工具提供参数来自定义文档处理并控制返回数据的详细程度。

> **唯一必填参数是 `file`** —— 您要处理的文件。

---

### 主要参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --------- | ---- | -------- | ------- | ---------- |
| `file` | file | **是** | - | 要解析的文件（支持 PDF、WORD、EXCEL、PPT、图片等） |
| `pdf_pwd` | string | 否 | - | 加密 PDF 文件的密码 |
| `page_ranges` | string | 否 | - | 指定要解析的页面范围。格式：`"1-2"` 表示第 1-2 页，`"1-2,3-4,5-10"` 表示多个范围 |

---

### Capabilities 参数

控制响应中包含哪些附加信息：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --------- | ---- | -------- | ------- | ---------- |
| `include_hierarchy` | boolean | 否 | `true` | 是否返回元素层级关系（parent_id、children_ids、ref_element_id），用于构建文档结构图谱 |
| `include_inline_objects` | boolean | 否 | `false` | 是否返回细粒度行内对象（公式、手写、复选框、文本中的图片） |
| `include_char_details` | boolean | 否 | `false` | 是否返回字符级详细信息（坐标、置信度、候选字符） |
| `include_image_data` | boolean | 否 | `false` | 是否返回图片数据（image_url、mime_type、base64）。启用后，base64 图片会自动上传到 Dify |
| `include_table_structure` | boolean | 否 | `false` | 是否返回详细的表格结构（JSON 格式：行、列、单元格及坐标和内容） |
| `pages` | boolean | 否 | `false` | 是否返回页面元信息列表（页面尺寸、page_image_url、每页的 element_ids） |
| `title_tree` | boolean | 否 | `false` | 是否返回层级标题树（目录） |
| `table_view` | select | 否 | `html` | Markdown 中表格的格式。选项：`markdown`（简单）、`html`（支持合并单元格的复杂表格） |

---

## API 限制

| 限制项 | 免费 API | 付费 API |
|--------|----------|----------|
| 支持格式 | PDF、图片（JPG/PNG/BMP/TIFF/WebP） | 20+ 格式（PDF、图片、Word、Excel、PPT、HTML、OFD 等） |
| 每日用量 | 1000 页 | 按套餐 |
| 文件大小 | 10MB | 500MB |
| PDF 页数 | — | 1000 页 |
| XLS/XLSX/CSV | — | 每 sheet ≤ 2000 行 × 100 列 |
| TXT | — | ≤ 100KB |
| 图片尺寸 | 20～20000 像素 | 20～20000 像素 |

---

## 注意事项

- 有关 capabilities 和参数的更多详情，请参阅 [解析配置文档](https://docs.textin.com/xparse/v1/parse-config)。
- 仅启用需要的 capabilities 以优化性能和响应大小。
- 默认值已针对常见用例进行优化。

---

## API 响应结构

### 顶级输出变量

工具返回包含以下输出变量的结构化数据：

| 变量 | 类型 | 说明 |
| -------- | ---- | ----------- |
| `text` | string | Markdown 格式的完整文档内容（来自 API 的 `markdown` 字段） |
| `elements` | array of object | 从文档中提取的结构化元素列表 |
| `pages` | array of object | 页面元信息列表（仅在启用 `pages` capability 时返回） |
| `title_tree` | array of object | 层级标题树 / 目录（仅在启用 `title_tree` capability 时返回） |
| `images` | array of object | 上传到 Dify 的图片列表（仅在启用 `include_image_data` 且存在图片时返回） |

---

### 字段详情

#### text

- **类型：** string  
- **说明：**  
  Markdown 格式的完整文档内容。直接来自 API 的 `markdown` 字段，包含标题、段落、表格、图片等的正确格式。

#### elements

- **类型：** array of objects  
- **说明：**  
  从文档中提取的结构化元素列表。每个元素代表一个语义单元（标题、段落、表格、图片等），包含元数据。

每个元素对象包含：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `element_id` | string | 元素的唯一标识符 |
| `type` | string | 元素类型：`Title`、`NarrativeText`、`ListItem`、`Table`、`Image`、`Formula`、`Header`、`Footer`、`PageNumber`、`FigureCaption`、`TableCaption`、`PageBreak`、`CodeSnippet`、`UncategorizedText` |
| `sub_type` | string | 可选的子类型，用于进一步分类（例如 Image 的：`stamp`、`qrcode`、`barcode`、`chart`） |
| `text` | string | 元素的文本内容 |
| `page_number` | integer | 元素所在的页码（从 1 开始） |
| `coordinates` | array | 8 元素数组，表示归一化的四边形坐标 [x1,y1,x2,y2,x3,y3,x4,y4]，范围 [0,1] |
| `metadata` | object | 元素元数据（见下文） |
| `objects` | array | 元素内的行内对象（仅在启用 `include_inline_objects` 时） |
| `table_structure` | object | 表格结构详情（仅 Table 元素且启用 `include_table_structure` 时） |
| `char_details` | array | 字符级详细信息（仅在启用 `include_char_details` 时） |
| `image_data` | object | 图片数据（仅 Image 元素且启用 `include_image_data` 时） |

##### 元素 metadata

`metadata` 字段提供上下文信息：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `parent_id` | string | 父元素 ID（如果启用 `include_hierarchy`） |
| `children_ids` | array | 子元素 ID 列表（如果启用 `include_hierarchy`） |
| `category_depth` | integer | 同类型元素的嵌套深度（例如 0 表示 H1，1 表示 H2） |
| `ref_element_id` | string | 引用的元素 ID，例如链接图片到其标题（如果启用 `include_hierarchy`） |
| `is_continuation` | boolean | 是否从上一页继续 |
| `continuation_of` | string | 如果 `is_continuation` 为 true，则为继续的元素 ID |
| `has_inline_objects` | boolean | 是否包含行内对象 |
| `inline_object_types` | array | 存在的行内对象类型（例如 `["formula", "handwriting"]`） |
| `width` | integer | 图片宽度（像素，仅 Image 元素） |
| `height` | integer | 图片高度（像素，仅 Image 元素） |
| `data_source` | object | 数据源信息，包括协议、路径和 URL |

#### pages

- **类型：** array of objects  
- **说明：**  
  页面元信息列表（仅在启用 `pages` capability 时返回）。每个页面对象包含：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `page_number` | integer | 页码（从 1 开始） |
| `page_width` | number | 页面宽度（像素） |
| `page_height` | number | 页面高度（像素） |
| `page_image_url` | string | 渲染的页面图片 URL |
| `element_ids` | array | 该页上的元素 ID 列表（按阅读顺序） |
| `dpi` | integer | 渲染时使用的 DPI |
| `angle` | number | 页面旋转角度（0 为正常阅读方向，顺时针） |
| `status` | string | 页面处理状态 |

#### title_tree

- **类型：** array of objects  
- **说明：**  
  层级文档大纲（仅在启用 `title_tree` capability 时返回）。每个节点包含：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `element_id` | string | 对应 Title 元素的 element_id |
| `title` | string | 标题文本 |
| `level` | integer | 标题级别（1 是最高级，即 H1） |
| `page_number` | integer | 标题所在页码 |
| `children` | array | 嵌套的子标题节点 |

#### images

- **类型：** array of objects  
- **说明：**  
  上传到 Dify 文件系统的图片列表（仅在启用 `include_image_data` 且存在带 base64 数据的图片时返回）。每个图片对象包含：

| 字段 | 类型 | 说明 |
| ----- | ---- | ----------- |
| `id` | string | Dify 文件 ID |
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
  "text": "# 文档标题\n\n这是 Markdown 格式的文档内容...\n\n## 章节 1\n\n段落文本在此。\n\n<table>\n  <tr><th>列 1</th><th>列 2</th></tr>\n  <tr><td>数据 1</td><td>数据 2</td></tr>\n</table>",
  "elements": [
    {
      "element_id": "el_001",
      "type": "Title",
      "text": "文档标题",
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
      "text": "这是 Markdown 格式的文档内容...",
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
      "title": "文档标题",
      "level": 1,
      "page_number": 1,
      "children": [
        {
          "element_id": "el_003",
          "title": "章节 1",
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

## 典型工作流用例

1. **RAG 知识入库** — 上传 PDF 或 Office 文件 → 解析为 Markdown 和结构化元素 → 分块并索引到知识库。
2. **Agent 文档理解** — 让你的 Agent 通过结构化输出阅读合同、报告、手册和表单，而不是直接处理原始文件。
3. **结构化信息抽取** — 先解析文档，再将干净的文本块、表格和元数据传递到下游的抽取、摘要或决策节点。
4. **版面感知处理** — 利用标题、页面坐标、表格和图片块支持更精准的检索、路由和文档自动化。

---

## 使用方法

1. 在 Dify 中安装此插件
2. 配置提供商 — 留空凭证使用免费 API，或填入凭证使用付费 API
3. 在工作流或智能体应用中使用解析工具
4. 上传文件并配置解析参数
5. 在下游节点中使用返回的 `text`、`elements` 和 `images`

---

## API 参考

- [Parse Sync API](https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync)
- [解析配置文档](https://docs.textin.com/xparse/v1/parse-config)
- [解析响应文档](https://docs.textin.com/xparse/v1/parse-response)

---

## 注意事项

- `text` 字段适合直接展示或作为 LLM 输入。
- `elements` 字段适用于结构化处理、分块、高亮和进一步分析。
- `images` 字段提供图片资源，用于预览或多模态工作流。
- `pages` 和 `title_tree` 字段提供文档结构洞察。
- 启用 `include_image_data` 时，带 base64 数据的图片会自动上传到 Dify 文件系统，`images` 数组包含上传的文件信息。
- 坐标已归一化到 [0, 1] 范围，相对于页面尺寸。要转换为像素，乘以页面宽度/高度。

---

标签：RAG、Agent、文档解析、结构化抽取、知识入库、PDF 解析、Markdown、表格、版面解析
