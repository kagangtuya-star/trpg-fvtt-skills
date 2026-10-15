# 示例：目标点吸引与终端坍缩

适用输入：用户描述《咒术回战》“术式顺转·苍”或相似的蓝色空间吸引，并希望采用约 1.6 秒、目标点锚定、最终压缩成小球的设计。

这是具体设计示例，不是所有同名招式或吸引特效的默认规格。若用户只提供名称，其中的时长、终态和播放尺寸应说明为设计建议；若用户已明确提供这些参数，则直接保留。

```text
Create a high-quality transparent WebM VFX for Foundry VTT representing Cursed Technique Lapse: Blue.

Effect identity and anchoring:
- Center the effect on a chosen target/location point in space, rather than on the caster.
- Keep all inward trajectories aligned with a stable visual center at normalized canvas position (0.5, 0.5).
- The defining impression is space being compressed into a single point. Convey attraction through shrinking distances and accelerating inward motion, rather than sustained circular orbiting.

Animation design:
- Total duration: approximately 1.6 seconds at 30 FPS, about 48 frames. Non-looping.
- From 0.0 to 1.5 seconds, sustain an intense inward attraction field.
- Surrounding energy, glowing particles, warped streaks, and spatial lines must visibly curve and accelerate toward the center.
- Combine multiple collapsing blue and cyan rings with inward-moving particles, curved radial streaks, and a dark-blue spatial pressure field. Stagger the layers so they do not collapse as a single flat symbol.
- During the final third of the animation, approximately 1.07 to 1.6 seconds, increase the apparent attraction strength and inward speed. Concentrate structure and brightness toward the core as the surrounding field contracts.
- During the final 0.1 second, approximately the last 3 frames, all visual structures must suddenly collapse into a very small, extremely bright blue-white sphere at the same center.
- The terminal sphere must feel dense, dangerous, and over-compressed, with a brief white-hot flash confined to the core. End on this compact terminal event without adding an outward detonation or a long trailing fade.

Visual quality:
- Maintain strong readability on dark, high-texture battle maps.
- Use a bright blue-white core, cyan intermediate structures, and deep-blue outer layers.
- Produce strong glow and an additive-light appearance while preserving the core silhouette, curved trajectories, and negative space.
- Build depth through layered compression structures, varied streak widths, particle sizes, brightness, and occlusion. Do not rely on thin circles alone.
- Suggest spatial distortion through warped structures inside the asset; the WebM itself is not expected to refract or displace the underlying battle map.
- The result should read as a powerful anime-style spatial technique, with clear transparent margins around all visible structures, including glow.

Avoid:
- Large explosions, outward particles, outward shockwaves, or fire-like motion.
- A generic wind vortex, a flat blue magic circle, HUD-style geometry, or a UI loading animation.
- Uniform-speed orbiting, thin-ring-only construction, excessive bloom that erases structure, or opaque background plates.

FVTT requirements and delivery:
- True transparent background; VP9 Alpha WebM with no audio.
- Canvas: 1024x1024. Frame rate: 30 FPS. Non-looping.
- Target/location anchored, with the visual anchor at the canvas center. Preserve this playback intent in the delivery notes.
- Recommended Sequencer playback size: approximately 4 to 5 grid units in visual diameter. This is a visual scale recommendation, not a rules-based damage area.
- Maintain readability when the playback is configured above lighting and darkness layers. Layer placement is an FVTT / Sequencer integration requirement, not behavior embedded in the WebM.
- Generate the WebM, a checkerboard preview/contact sheet, and a manifest with actual dimensions, FPS, duration, loop state, visual anchor, and recommended playback size. Keep the checkerboard out of the WebM.
- Use fvtt-webm-vfx's forced high-quality rendering pipeline when available: at least 2x supersampling followed by downsampling and high-quality VP9 Alpha encoding. If using another renderer, retain the same quality requirements.
- Do not use a fast, draft, placeholder, or low-quality renderer.
- Verify transparency, clear margins, inward motion, phase timing, and the compact terminal event. Report any renderer limitation rather than replacing the intended motion with a generic substitute. Distinguish encoding checks from actual FVTT playback validation.
```

## 此例的优化重点

- **锚点先于装饰**：目标位置与画布中心分别明确，全部向心运动共用中心。
- **时间对应动作**：1.5 秒吸引与 0.1 秒终态覆盖总时长；最后三分之一是叠加的加速区间。
- **负面约束服务身份**：排除外扩、风旋和 HUD，是为了保护空间压缩主题；这些禁项不应迁移到爆炸或法阵任务。
- **实现边界可交接**：地图扭曲、播放层级与场景照明不被误写成视频本身的能力；高质量要求和文件交付可由独立渲染技能承接。
