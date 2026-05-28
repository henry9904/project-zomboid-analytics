-- Logs zombies within 50 cells of the player every 6 in-game hours.
-- Throttled to avoid stalling the main thread on dense outdoor maps.
require "DataDumper_Init"

local TICK_COUNTER = 0
local LOG_EVERY    = 3  -- 3 * 2h tick = every 6 in-game hours
local RADIUS       = 50 -- cells

local function logZombies()
    TICK_COUNTER = TICK_COUNTER + 1
    if TICK_COUNTER % LOG_EVERY ~= 0 then return end

    local cell = getCell()
    if cell == nil then return end
    local zlist = cell:getZombieList()
    if zlist == nil then return end

    local player = getSpecificPlayer(0)
    if player == nil then return end
    local px, py = player:getX(), player:getY()
    local age = getGameTime():getWorldAgeHours()

    for i = 0, zlist:size() - 1 do
        local z = zlist:get(i)
        local zx, zy = z:getX(), z:getY()
        if math.abs(zx - px) < RADIUS and math.abs(zy - py) < RADIUS then
            local line = string.format(
                "%.3f,%.2f,%.2f,%d,%s",
                age, zx, zy, z:getZ(), tostring(z:getMoveState())
            )
            DataDumper.writeLine(DataDumper.ZOMBIE_LOG, line)
        end
    end
end

Events.OnTickEvenHours.Add(logZombies)
