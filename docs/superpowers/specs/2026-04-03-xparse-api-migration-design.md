# xParse API Migration Design

**Date:** 2026-04-03  
**Version:** 1.2.0  
**Status:** Approved

## Overview

Migrate the xParse Dify plugin from the legacy Pipeline API to the new Parse Sync API (v1.3.0). This is a breaking change that simplifies the plugin by removing deprecated parameters and adopting the new API's native structure.

## Background

The xParse API has undergone a major revision with a new endpoint, parameter structure, and response format. The current plugin uses the legacy `/api/xparse/pipeline` endpoint with a stages-based configuration. The new API uses `/api/v1/xparse/parse/sync` with a streamlined config object.

**Key Reference Documents:**
- New API OpenAPI spec: `.tasks/parse-sync.openapi.yaml`
- Parameter documentation: `.tasks/parse-config.mdx`
- Response documentation: `.tasks/parse-response.mdx`
- Remote docs: https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync

## Design Decisions

### 1. Parameter Strategy

**Decision:** Complete removal of legacy parameters, full exposure of new capabilities.

**Rationale:**
- Clean break from legacy API eliminates maintenance burden
- Users need full control over capabilities for different use cases
- Version bump to 1.2.0 signals breaking change

**Removed Parameters:**
- `provider` - not exposed (always use textin internally)
- `crop_dewarp` - not in new API
- `remove_watermark` - not in new API
- `get_page_image` - replaced by `pages` capability
- `get_sub_image` - replaced by `include_image_data` capability
- `parse_mode` - not in new API
- `underline_level` - not in new API
- `apply_chart` - not in new API
- `image_storage_config` - not in new API

**New Parameters (capabilities):**
- `include_hierarchy` (boolean, default: true)
- `include_inline_objects` (boolean, default: false)
- `include_char_details` (boolean, default: false)
- `include_image_data` (boolean, default: false)
- `include_table_structure` (boolean, default: false)
- `pages` (boolean, default: false)
- `title_tree` (boolean, default: false)
- `table_view` (select: markdown/html, default: html)

**Retained Parameters (remapped):**
- `file` → `file` (unchanged)
- `pdf_pwd` → `document.password`
- `page_ranges` → `scope.page_range`

### 2. Output Structure

**Decision:** Use new API's native structure directly.

**Rationale:**
- Cleaner, more maintainable code
- Users get access to full API capabilities
- Avoids unnecessary transformation logic

**Output Variables:**
- `text` - sourced from `data.markdown` (not self-constructed)
- `elements` - `data.elements` (native structure)
- `pages` - `data.pages` (if capability enabled)
- `title_tree` - `data.title_tree` (if capability enabled)
- `images` - array of uploaded image objects (if `include_image_data` enabled)

### 3. Architecture Approach

**Decision:** Minimal change approach - keep existing file structure, rewrite core methods.

**Rationale:**
- Lower risk than full refactor
- Focused testing surface
- Quick delivery

**Files to Modify:**
- `tools/parse.py` - core implementation
- `tools/parse.yaml` - parameter definitions
- `README.md` - documentation with remote links
- `provider/xparse.yaml` - version bump to 1.2.0

**Methods to Rewrite:**
- `_build_parse_config()` - construct new config structure
- `_invoke()` - request building and response processing

**Methods Unchanged:**
- `_get_credentials()` - credential handling
- `validate_api_credentials()` - validation logic

## Technical Design

### API Endpoint

```python
OLD: "https://api.textin.com/api/xparse/pipeline"
NEW: "https://api.textin.com/api/v1/xparse/parse/sync"
```

### Request Structure

**Old (stages-based):**
```python
stages = [{"type": "parse", "config": {...}}]
files = {
    "file": (filename, blob, mime_type),
    "stages": (None, json.dumps(stages), "application/json")
}
```

**New (direct config):**
```python
config = {
    "document": {"password": "..."},  # optional
    "capabilities": {
        "include_hierarchy": true,
        "include_inline_objects": false,
        # ...
    },
    "scope": {"page_range": "1-5"}  # optional
}
files = {
    "file": (filename, blob, mime_type),
    "config": (None, json.dumps(config), "application/json")
}
```

### Config Builder Implementation

```python
def _build_parse_config(self, tool_parameters: dict[str, Any]) -> dict[str, Any]:
    """Build parse configuration from tool parameters."""
    config = {}
    
    # document section (optional)
    if tool_parameters.get("pdf_pwd"):
        config["document"] = {
            "password": tool_parameters["pdf_pwd"]
        }
    
    # capabilities section (always present)
    config["capabilities"] = {
        "include_hierarchy": tool_parameters.get("include_hierarchy", True),
        "include_inline_objects": tool_parameters.get("include_inline_objects", False),
        "include_char_details": tool_parameters.get("include_char_details", False),
        "include_image_data": tool_parameters.get("include_image_data", False),
        "include_table_structure": tool_parameters.get("include_table_structure", False),
        "pages": tool_parameters.get("pages", False),
        "title_tree": tool_parameters.get("title_tree", False),
        "table_view": tool_parameters.get("table_view", "html"),
    }
    
    # scope section (optional)
    if tool_parameters.get("page_ranges"):
        config["scope"] = {
            "page_range": tool_parameters["page_ranges"]
        }
    
    return config
```

### Response Structure

**New API Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "schema_version": "1.3.0",
    "file_id": "doc_7f3a2b",
    "job_id": "job_x9k2m",
    "success_count": 2,
    "metadata": {
      "filename": "document.pdf",
      "filetype": "application/pdf",
      "page_count": 10,
      "data_source": {...}
    },
    "markdown": "# Title\n\nContent...",
    "elements": [...],
    "title_tree": [...],  // if capability enabled
    "pages": [...]        // if capability enabled
  }
}
```

### Response Processing Logic

1. **Extract data**
   ```python
   data = result.get("data", {})
   markdown = data.get("markdown", "")
   elements = data.get("elements", [])
   pages = data.get("pages", [])
   title_tree = data.get("title_tree", [])
   ```

2. **Process images (if include_image_data enabled)**
   - Find Image type elements with `image_data.base64`
   - Decode and upload to Dify file system
   - Update element metadata with `preview_url` and `dify_file_id`
   - Remove `base64` field to reduce response size
   - Collect uploaded images for `images` output variable

3. **Yield outputs**
   ```python
   yield self.create_text_message(markdown)
   yield self.create_variable_message("elements", elements)
   if pages:
       yield self.create_variable_message("pages", pages)
   if title_tree:
       yield self.create_variable_message("title_tree", title_tree)
   if images:
       yield self.create_variable_message("images", images)
   ```

### Image Processing Details

When `include_image_data=true`:

1. **Image elements** will have `image_data` field:
   ```json
   {
     "image_url": "https://...",
     "mime_type": "image/png",
     "base64": "iVBORw0KGgoAAAA..."  // optional
   }
   ```

2. **Processing flow:**
   ```python
   if element.get("type") == "Image" and element.get("image_data"):
       image_data = element["image_data"]
       
       # If base64 present, upload to Dify
       if image_data.get("base64"):
           image_bytes = base64.b64decode(image_data["base64"])
           mime_type = image_data.get("mime_type", "image/png")
           
           file_res = self.session.file.upload(
               element.get("element_id", "image"),
               image_bytes,
               mimetype=mime_type
           )
           
           images.append(file_res)
           element["image_data"]["preview_url"] = file_res.preview_url
           element["image_data"]["dify_file_id"] = file_res.id
           del element["image_data"]["base64"]  # Remove to reduce size
   ```

### Error Handling

Maintain existing error handling patterns:

1. **HTTP errors**: `requests.exceptions.RequestException`
2. **API errors**: Check `result.get("code") != 200`
3. **Data errors**: Defensive programming with `.get()` and default values
4. **Logging**: Use `logger.exception()` for detailed error traces

Error response format:
```json
{
  "code": 40004,
  "message": "参数错误，请查看技术文档，检查传参",
  "location": {
    "stage": "parse",
    "page_number": 3,
    "element_id": "el_045"
  }
}
```

## Data Flow

```
User Input (Dify)
  ↓
Tool Parameters (parse.yaml)
  ↓
_build_parse_config() → config object
  ↓
API Request (multipart/form-data)
  ↓
Parse Sync API (v1.3.0)
  ↓
API Response (JSON)
  ↓
Response Processing
  ├── Extract markdown → text output
  ├── Extract elements → elements output
  ├── Process images (if enabled) → images output
  ├── Extract pages (if enabled) → pages output
  └── Extract title_tree (if enabled) → title_tree output
  ↓
Yield ToolInvokeMessage(s)
  ↓
Dify Workflow/Agent
```

## Testing Strategy

### Unit Tests
- Config builder with various parameter combinations
- Image processing logic
- Error handling paths

### Integration Tests
- API call with real credentials
- File upload handling
- Response parsing

### Manual Tests
- All capability combinations
- PDF with password
- Page range filtering
- Image data upload to Dify
- Error scenarios (invalid credentials, bad parameters)

## Documentation Updates

### README.md
- Replace Pipeline API references with Parse Sync API
- Update parameter documentation
- Use remote documentation links:
  - API reference: https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync
  - Config guide: https://docs.textin.com/xparse/v1/parse-config
  - Response guide: https://docs.textin.com/xparse/v1/parse-response
- Update example responses to match new structure
- Document breaking changes from 1.0.0 to 1.2.0

### parse.yaml
- Remove deprecated parameter definitions
- Add new capability parameters
- Update descriptions to reference new API behavior

## Migration Notes for Users

**Breaking Changes in v1.2.0:**

1. **Removed parameters**: `crop_dewarp`, `remove_watermark`, `get_page_image`, `get_sub_image`, `parse_mode`, `underline_level`, `apply_chart`, `image_storage_config`, `provider`

2. **New parameters**: `include_hierarchy`, `include_inline_objects`, `include_char_details`, `include_image_data`, `include_table_structure`, `pages`, `title_tree`, `table_view`

3. **Output structure changes**:
   - `text` now comes from API's markdown field (not self-constructed)
   - `elements` structure updated to match new API schema
   - New output variables: `pages`, `title_tree`

4. **Migration guide**:
   - `get_page_image=true` → use `pages=true`
   - `get_sub_image=true` → use `include_image_data=true`
   - Other removed parameters have no direct equivalent

## Implementation Checklist

- [ ] Update API endpoint URL constant
- [ ] Rewrite `_build_parse_config()` method
- [ ] Update request construction in `_invoke()`
- [ ] Rewrite response processing logic
- [ ] Update `parse.yaml` with new parameters
- [ ] Remove old parameter definitions from `parse.yaml`
- [ ] Update README.md with new documentation
- [ ] Update version to 1.2.0 in `provider/xparse.yaml`
- [ ] Test with various parameter combinations
- [ ] Test image upload functionality
- [ ] Verify error handling
- [ ] Create commit with clear breaking change message

## Success Criteria

1. Plugin successfully calls new Parse Sync API
2. All new capability parameters work as expected
3. Image upload to Dify works when `include_image_data=true`
4. Pages and title_tree returned when enabled
5. Error handling gracefully handles API errors
6. Documentation accurately reflects new behavior
7. No references to deprecated parameters remain
8. Version bumped to 1.2.0

## Risk Assessment

**Low Risk:**
- API endpoint change (straightforward)
- Config structure (well-documented)
- Response structure (clear schema)

**Medium Risk:**
- Image processing logic (depends on Dify file upload API)
- Breaking changes may affect existing users

**Mitigation:**
- Comprehensive testing before release
- Clear documentation of breaking changes
- Version bump signals major change

## Timeline

**Estimated effort:** 4-6 hours

1. Code changes: 2-3 hours
2. Testing: 1-2 hours
3. Documentation: 1 hour
4. Review and polish: 30 minutes

## References

- [Parse Sync API OpenAPI Spec](.tasks/parse-sync.openapi.yaml)
- [Parse Config Documentation](.tasks/parse-config.mdx)
- [Parse Response Documentation](.tasks/parse-response.mdx)
- [Remote API Documentation](https://docs.textin.com/api-reference/endpoint/xparse/v1/parse-sync)
