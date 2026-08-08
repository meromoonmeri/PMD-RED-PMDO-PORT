--- PMDO AUTOMATIC CONVERSION
--- Source Scene: d13p03

local d13p03 = {}

function d13p03.Cutscene()
  GAME:CutsceneMode(true)

  GAME:FadeOutBGM(60)
  GAME:WaitFrames(60)
  GAME:PlayBGM('Rayquazas Domain', true)
  -- [PMDO] TODO: GAME:MoveCamera(HeroX, HeroY, 1)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  GAME:FadeOut(true, 8) -- FLASH_TO equivalent
  GAME:FadeIn(8) -- FLASH_FROM equivalent
  GAME:FadeOut(true, 8) -- FLASH_TO equivalent
  GAME:FadeIn(8) -- FLASH_FROM equivalent
  SOUND:PlayBattleSE('EVT_Roar')
  GAME:WaitFrames(20) -- SCREEN_SHAKE equivalent
  GAME:FadeOut(true, 30) -- FLASH_TO equivalent
  GAME:FadeIn(16) -- FLASH_FROM equivalent
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:9)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:23)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:22)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:23)
  GAME:FadeOut(true, 8) -- FLASH_TO equivalent
  GAME:FadeIn(8) -- FLASH_FROM equivalent
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:24)
  GAME:FadeOut(true, 4) -- FLASH_TO equivalent
  GAME:FadeIn(4) -- FLASH_FROM equivalent
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:25)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  GAME:PlayBGM('Rayquazas Domain', true)
  GAME:FadeOut(true, 16) -- FLASH_TO equivalent
  -- [PMDO] TODO: GAME:MoveCamera(HeroX, HeroY, 1)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  GAME:FadeOutBGM(120)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  SOUND:PlayBattleSE('EVT_Roar')
  GAME:WaitFrames(20) -- SCREEN_SHAKE equivalent
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:24)
  GAME:PlayBGM('Rayquazas Domain', true)
  GAME:FadeIn(16) -- FLASH_FROM equivalent
  GAME:FadeOutBGM(60)
  GAME:FadeOut(true, 60) -- FLASH_TO equivalent
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)
  -- [PMDO] TODO: GROUND:CharSetAction(target, AnimId:2)

  GAME:CutsceneMode(false)
end

return d13p03
