# Bug Fix: Insights Page Technical Details Checkbox

## Issue
When clicking the "Show Technical Details" checkbox in the Insights tab, the screen would become blank with no data displayed.

## Root Cause
The rendering logic for technical details was not properly validating that `evidence` was an array before calling `.map()` on it. While the `formatEvidence()` function returns either `null` or an array, the conditional rendering only checked `evidence && evidence.length > 0`, which could fail in edge cases.

Additionally, if any evidence value was `null` or `undefined`, attempting to render it directly could cause rendering errors.

## Fix Applied

### File: `/frontend/echo-bi/src/pages/InsightsPage.jsx`

**Lines 703-730** - Added defensive checks:
```jsx
// BEFORE:
{(showTechnicalDetails || isExpanded) && evidence && evidence.length > 0 && (

// AFTER:
{(showTechnicalDetails || isExpanded) && evidence && Array.isArray(evidence) && evidence.length > 0 && (
```

**Lines 721** - Added safe value rendering:
```jsx
// BEFORE:
<span className="evidence-value">{value}</span>

// AFTER:
<span className="evidence-value">{value ? String(value) : ''}</span>
```

**Lines 735-742** - Added same defensive checks to expand button:
```jsx
// BEFORE:
{!showTechnicalDetails && evidence && evidence.length > 0 && (

// AFTER:
{!showTechnicalDetails && evidence && Array.isArray(evidence) && evidence.length > 0 && (
```

## Changes Summary

1. **Added `Array.isArray(evidence)` check** - Ensures evidence is actually an array before attempting to map over it
2. **Added `String(value)` conversion** - Safely converts evidence values to strings even if they're null/undefined
3. **Applied defensive checks consistently** - Both technical details section and expand button now have proper validation

## Testing

To test the fix:

1. Upload a dataset and navigate to the Insights page
2. Generate insights by clicking "🚀 Generate Insights"
3. Click the "Show Technical Details" checkbox in the header
4. Verify that:
   - The page doesn't go blank
   - Technical details appear for all insights (if evidence is available)
   - All evidence values render correctly
5. Uncheck the checkbox
6. Verify individual expand/collapse buttons work correctly

## Impact

- **Low Risk** - Only adds defensive checks, doesn't change core logic
- **High Value** - Prevents blank screen errors when toggling technical details
- **Backward Compatible** - Works with existing data structures

## Related Files

- `/frontend/echo-bi/src/pages/InsightsPage.jsx` - Main fix location
- No backend changes required

## Date

February 5, 2026
