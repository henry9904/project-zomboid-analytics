-- Logs player vitals + nutrition every 2 in-game hours.
require "DataDumper_Init"

local function logPlayerStats()
    local player = getSpecificPlayer(0)
    if player == nil then return end
    local stats = player:getStats()
    local nutri = player:getNutrition()
    local gt    = getGameTime()
    local line = string.format(
        "%.3f,%d,%.2f,%.2f,%.2f,%d,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.1f,%.2f,%.2f,%.2f,%.2f",
        gt:getWorldAgeHours(),
        gt:getNightsSurvived(),
        gt:getTimeOfDay(),
        player:getX(), player:getY(), player:getZ(),
        stats:getHunger(), stats:getThirst(), stats:getFatigue(),
        stats:getStress(), stats:getPanic(), stats:getBoredom(),
        nutri:getCalories(), nutri:getWeight(),
        nutri:getCarbohydrates(), nutri:getProteins(), nutri:getLipids()
    )
    DataDumper.writeLine(DataDumper.PLAYER_LOG, line)
end

Events.OnTickEvenHours.Add(logPlayerStats)
