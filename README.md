# 这是一个使用WebView实现的Phigros谱面的模拟器

## 环境配置

- Python 版本: `3.12.8`
- Windows 版本需 >= `8.1`
- 第三方库: [requirements.txt](./src/requirements.txt)

## 谱面兼容

- [x] phi
  - [x] formatVersion
    - [x] 1
    - [x] 3
  - [x] offset
  - [x] judgeLineList
    - [x] bpm
    - [x] notesAbove
    - [x] notesBelow
    - [x] speedEvents
    - [x] judgeLineMoveEvents
    - [x] judgeLineRotateEvents
    - [x] judgeLineDisappearEvents
- [ ] rpe
  - [x] BPMList
  - [ ] META (无法获取info文件时读取)
    - [x] RPEVersion (???, 参见 RPEVersion 特殊处理)
    - [x] background
    - [x] charter
    - [x] composer
    - [ ] id
    - [x] level
    - [x] name
    - [x] offset
    - [x] song
  - [ ] judgeLineList
    - [x] Texture
    - [x] bpmfactor (?, 按照字母意思: bpm速率进行处理)
    - [x] father
    - [x] isCover
    - [x] isGif
    - [x] eventLayers
      - [ ] gifEvents (???)
      - [x] alphaEvents
      - [x] moveXEvents
      - [x] moveYEvents
      - [x] rotateEvents
      - [x] speedEvents
    - [ ] extended
      - [x] colorEvents
      - [ ] inclineEvents (???)
      - [x] scaleXEvents
      - [x] scaleYEvents
      - [ ] paintEvents (???)
      - [x] textEvents
    - [x] notes
      - [x] startTime
      - [x] endTime
      - [x] above
      - [x] alpha
      - [x] isFake
      - [x] positionX
      - [x] size
      - [x] speed
      - [x] type
      - [x] visibleTime
      - [x] yOffset
      - [x] hitsound
    - [x] alphaControl (可能有bug)
    - [x] posControl (可能有bug)
    - [x] sizeControl (可能有bug)
    - [ ] skewControl (???)
    - [x] yControl (可能有bug)
    - [x] zOrder
- [x] pec
  - 读取转换为`rpe`格式
- [ ] phira resource pack
  - [x] click.png
  - [x] click_mh.png
  - [x] drag.png
  - [x] drag_mh.png
  - [x] hold.png
  - [x] hold_mh.png
  - [x] flick.png
  - [x] flick_mh.png
  - [x] hit_fx.png
  - [x] click.ogg
  - [x] drag.ogg
  - [x] flick.ogg
  - [ ] ending.mp3
  - [ ] info.yml
    - [ ] name
    - [ ] author
    - [ ] description
    - [x] hitFx
    - [x] holdAtlas
    - [x] holdAtlasMH
    - [x] hitFxDuration
    - [x] hitFxScale
    - [ ] hitFxRotate
    - [x] hitFxTinted
    - [x] hideParticles
    - [x] holdKeepHead
    - [ ] holdRepeat
    - [ ] holdCompact
    - [x] colorPerfect
    - [x] colorGood

### RPEVersion 特殊处理

- `>= 150` 时, `textEvents` 中的 `\n` 才生效, 否则使用 `webview` 默认行为

## 声明

- 此项目仅用于学习交流，请勿用于商业用途
