-- PlayerStatsLogger: logs player stats + nutrition every 2 game-hours
-- Output: datadumper_player_stats.csv

local function logPlayerStats()
    local player = getSpecificPlayer(0)
    if not player then return end

    local stats     = player:getStats()
    local nutrition = player:getNutrition()
    local gt        = getGameTime()
    local ts        = string.format("%.2f", gt:getWorldAgeHours())
    local day       = tostring(gt:getNightsSurvived())
    local hour      = string.format("%.2f", gt:getTimeOfDay())
    local x = string.format("%.1f", player:getX())
    local y = string.format("%.1f", player:getY())
    local z = string.format("%.1f", player:getZ())

    local line = table.concat({
        ts, day, hour, x, y, z,
        string.format("%.4f", stats:getHunger()),
        string.format("%.4f", stats:getThirst()),
        string.format("%.4f", stats:getFatigue()),
        string.format("%.4f", stats:getStress()),
        string.format("%.4f", stats:getPanic()),
        string.format("%.4f", stats:getBoredom()),
        string.format("%.2f", nutrition:getCalories()),
        string.format("%.2f", nutrition:getWeight()),
        string.format("%.2f", nutrition:getCarbohydrates()),
        string.format("%.2f", nutrition:getProteins()),
        string.format("%.2f", nutrition:getLipids()),
    }, ",")

    DataDumper.writeCSVLine("datadumper_player_stats.csv", line)
end

Events.OnTickEvenHours.Add(logPlayerStats)
