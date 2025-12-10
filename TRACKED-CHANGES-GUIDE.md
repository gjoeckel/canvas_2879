# Tracked Changes Guide

## Understanding the "No tracked changes found" Message

If you see:
```
Found 0 insertions and 0 deletions
ℹ️ No tracked changes found in DOCX file.
```

This means the DOCX file doesn't contain any tracked changes. Here's why and how to fix it:

## Why No Tracked Changes?

### 1. Track Changes Not Enabled
**Problem:** "Track Changes" feature is not enabled in Microsoft Word.

**Solution:**
1. Open the DOCX file in Microsoft Word
2. Go to the **Review** tab
3. Click **Track Changes** button (or press `Ctrl+Shift+E` / `Cmd+Shift+E`)
4. Make your edits - they will now be tracked
5. Save the file
6. Upload to Box

### 2. All Changes Already Accepted/Rejected
**Problem:** The document had tracked changes, but they were all accepted or rejected.

**Solution:**
- Make new edits with Track Changes enabled
- Or revert to a previous version that has tracked changes

### 3. Document Never Had Edits
**Problem:** The document hasn't been edited since Track Changes was enabled.

**Solution:**
- Make some test edits (add text, delete text) with Track Changes enabled
- Save and upload to Box

## How to Enable Track Changes in Word

### Microsoft Word (Windows/Mac)

1. **Open the document** in Microsoft Word
2. **Go to Review tab**
3. **Click "Track Changes"** button
   - The button should be highlighted/active when tracking is on
4. **Make your edits:**
   - **Insertions** will appear in a different color (usually red/green)
   - **Deletions** will appear with strikethrough
5. **Save the document**
6. **Upload to Box**

### Microsoft Word Online (Box Office Online)

1. **Open the document** in Box Office Online
2. **Click "Review"** in the ribbon
3. **Click "Track Changes"** 
4. **Make your edits**
5. **Save** (changes are automatically saved in Box)

## Testing Tracked Changes

To test if tracked changes are working:

1. **Enable Track Changes** in Word
2. **Add some text** (e.g., "This is a test addition")
3. **Delete some text** (select and delete existing text)
4. **Save the document**
5. **Try the "update canvas" button again**

You should now see:
```
Found X insertions and Y deletions
```

## What Gets Tracked?

- ✅ **Text insertions** - New text you add
- ✅ **Text deletions** - Text you delete (shown with strikethrough)
- ❌ **Formatting changes** - Usually not tracked (font, color, etc.)
- ❌ **Accepted changes** - Once accepted, they're no longer "tracked"

## Next Steps

1. **Enable Track Changes** in your DOCX file
2. **Make some edits** to test
3. **Save and upload** to Box
4. **Try "update canvas" again**

The system will now detect and apply your tracked changes!

