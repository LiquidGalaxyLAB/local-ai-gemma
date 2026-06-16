# KML Validation Checklist for Liquid Galaxy

Use this checklist to validate KML files before deployment to Liquid Galaxy rigs.

## Pre-deployment Validation

### 1. Syntax Check
- [ ] File passes `xmllint --noout file.kml` without errors
- [ ] XML is well-formed with proper tag closure
- [ ] Root element is `<kml>` with correct namespace

### 2. Structure Check
- [ ] Contains `<Document>` element as direct child of `<kml>`
- [ ] Document contains required metadata: `<name>`, `<description>` (optional but recommended)
- [ ] All `<Placemark>` elements are properly nested within `<Document>`
- [ ] Each Placemark has: `<name>`, `<description>` (optional), `<styleUrl>` (optional), and geometry

### 3. Geometry Validation
- [ ] Coordinates are in correct order: longitude,latitude[,altitude]
- [ ] Longitude values are between -180 and 180
- [ ] Latitude values are between -90 and 90
- [ ] Altitude values are reasonable for use case (typically 0 for ground-level)
- [ ] All coordinate triples are separated by spaces
- [ ] No missing or extra coordinates in geometries

### 4. Style Validation
- [ ] All referenced `<styleUrl>` values correspond to defined `<Style>` elements
- [ ] Style IDs are prefixed with `#` in styleUrl references
- [ ] Color values are in proper hex format: aabbggrr (Alpha, Blue, Green, Red)
- [ ] Alpha values: 00 (transparent) to ff (opaque)
- [ ] Scale values are positive numbers
- [ ] Line widths are positive numbers

### 5. Liquid Galaxy Specific Checks
- [ ] File size is reasonable (<5MB recommended for optimal performance)
- [ ] Geometry complexity is appropriate for real-time rendering
- [ ] Colors provide sufficient contrast for large screen viewing
- [ ] Point scales are adequate for visibility (typically 1.0-2.0)
- [ ] Line widths are visible but not overwhelming (typically 1.0-3.0)

## Deployment Verification

### 6. File Transfer
- [ ] File successfully copied to `/var/www/html/kmls/` on lg1
- [ ] File permissions allow reading by the web server process
- [ ] Owner/group settings are appropriate

### 7. Post-deployment Check
- [ ] File exists at expected path: `/var/www/html/kmls/your_file.kml`
- [ ] File content matches source (use diff or checksum)
- [ ] File is accessible via web server (if applicable)

### 8. Rendering Verification
- [ ] KML renders correctly on Liquid Galaxy after relaunch
- [ ] Geometry appears in expected location
- [ ] Styles (colors, icons, line widths) display as intended
- [ ] Labels are visible and legible
- [ ] No missing or distorted geometry

## Common Issues to Check

### Syntax Problems
- Missing closing tags
- Incorrect tag case (KML is case-sensitive)
- Improperly nested elements
- Invalid XML entities (use &lt; &gt; &amp; etc.)

### Coordinate Problems
- Latitude,longitude order instead of longitude,latitude
- Coordinates outside valid ranges
- Missing altitude values when required
- Extra spaces or characters in coordinate strings

### Style Problems
- Missing or incorrect style definitions
- Invalid color hex format
- Undefined style references
- Missing # prefix in styleUrl

### Performance Problems
- Excessively complex polygons (>1000 vertices)
- Extremely large file sizes (>10MB)
- Overly aggressive refresh rates that cause flickering

## Quick Validation Command

Run this command to perform basic validation:
```bash
# Check if xmllint is available
command -v xmllint || { echo "Please install libxml2-utils: sudo apt install libxml2-utils"; exit 1; }

# Validate the KML file
xmllint --noout "$1" && echo "✓ Syntax validation passed" || { echo "✗ Syntax validation failed"; exit 1; }

# Additional checks can be added here
echo "Validation complete. Please perform visual verification on Liquid Galaxy."
```