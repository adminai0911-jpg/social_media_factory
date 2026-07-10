# Video Pipeline Enhancements

The user has requested 5 specific enhancements to the viral video pipeline to improve the mid-video CTA, fix hook rendering colors, improve the Telegram alerts, and enforce a programmatic pixel-brightness QA gate on the final MP4.

## Proposed Changes

### 1. Fix Opening Hook Contrast & Unify Configurations
- **[MODIFY] `remotion-studio/src/MainVideo.tsx`**: Update the `ThumbnailCover` component and any remaining subtitle blocks to strictly use `CONFIG.COLORS.hookText`, `CONFIG.COLORS.hookHighlightBg`, and `CONFIG.COLORS.hookHighlightText` instead of the dynamic `pal` variables or hardcoded `#FFFFFF`. This guarantees that both the main video hook and the generated thumbnail cover follow the exact same high-contrast amber/navy logic.
- **[MODIFY] `remotion-studio/src/config.ts`**: Ensure the contrast colors are fully centralized and correct.

### 2. Add Mid-Video Comment Prompt (15s Mark)
- **[MODIFY] `orchestrator/v32_dopamine_engine.py`**: Update the LLM prompt to generate a new JSON key: `mid_video_cta`. The AI will generate a contextual 1-line prompt (e.g., "Comment '1' agar tumne bhi yeh mistake ki thi 👇").
- **[MODIFY] `remotion-studio/src/MainVideo.tsx`**: Render the `mid_video_cta` dynamically as a small pill/banner. It will be timed to appear exactly between `p_l1` and `p_l2` (around 15 seconds) for a duration of 2 seconds, ensuring it clears completely before the next rule card appears.

### 3. Telegram Linktree Reminder
- **[MODIFY] `uploader.py`**: Append the following reminder to the successful publish Telegram alert:
  `Reminder: verify bio link is live at instagram.com/wealth_matrix_ai before this reel reaches peak hours.`

### 4. Post-Render Pixel Brightness QA Gate
- **[MODIFY] `orchestrator/v32_dopamine_engine.py`**: After `remotion bundle` finishes, run a post-render validation check.
  - Use `ffmpeg` to extract frames from the first 3 seconds of the generated MP4.
  - Use Python (e.g., `PIL` or `cv2`) to compute the average brightness (0-255) of the central text region.
  - Reject the render (throw an exception) if the average brightness is below 80, and log the measured value in the QA results.

## User Review Required
> [!IMPORTANT]
> The post-render pixel QA gate will require extracting frames using `ffmpeg` and computing brightness. If the render fails this gate, the entire GitHub Actions pipeline will fail. Are you okay with this strict enforcement?

## Verification Plan
1. Trigger a dry run of the script generator to verify `mid_video_cta` is populated.
2. Render a test video via Remotion and verify the hook contrast is fixed across both the video and the thumbnail.
3. Validate the `uploader.py` logic sends the correct string.
4. Verify the post-render QA check correctly computes brightness and rejects/accepts based on the threshold.
