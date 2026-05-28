-- Captures player-emitted noise events. PZ doesn't expose a generic Events.OnNoise,
-- so we hook the player's weapon attack callback and infer intensity from the
-- weapon's SoundRadius. Extend with OnZombieDead etc. as needed.
require "DataDumper_Init"

local function logAttack(player, handWeapon)
    if player == nil or handWeapon == nil then return end
    local age = getGameTime():getWorldAgeHours()
    local x, y = player:getX(), player:getY()
    local kind = handWeapon:isAimedFirearm() and "gunshot" or "melee"
    local radius = handWeapon:getSoundRadius() or 0.0
    local line = string.format(
        "%.3f,%.2f,%.2f,%.2f,%s",
        age, x, y, radius, kind
    )
    DataDumper.writeLine(DataDumper.NOISE_LOG, line)
end

Events.OnPlayerAttackFinished.Add(logAttack)
