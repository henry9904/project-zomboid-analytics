-- ZombieLogger: samples zombie positions every 6 game-hours
-- Logs only zombies within 50 cells of player to limit volume
-- Output: datadumper_zombie_log.csv

local SAMPLE_RADIUS = 50  -- cells (1 cell = 10 in-game meters)
local SAMPLE_INTERVAL_HOURS = 6
local _lastSampleHour = -1

local function shouldSample()
    local currentHour = getGameTime():getWorldAgeHours()
    if currentHour - _lastSampleHour >= SAMPLE_INTERVAL_HOURS then
        _lastSampleHour = currentHour
        return true
    end
    return false
end

local function logZombies()
    if not shouldSample() then return end

    local player = getSpecificPlayer(0)
    if not player then return end

    local px, py = player:getX(), player:getY()
    local ts     = DataDumper.getTimestamp()
    local zombieList = getCell():getZombieList()
    local count  = 0

    for i = 0, zombieList:size() - 1 do
        local zombie = zombieList:get(i)
        local zx, zy = zombie:getX(), zombie:getY()

        -- distance filter: Manhattan for speed
        if math.abs(zx - px) <= SAMPLE_RADIUS and math.abs(zy - py) <= SAMPLE_RADIUS then
            local zz    = string.format("%.1f", zombie:getZ())
            local state = tostring(zombie:getActivityState())
            local line  = table.concat({
                ts,
                string.format("%.1f", zx),
                string.format("%.1f", zy),
                zz,
                state,
            }, ",")
            DataDumper.writeCSVLine("datadumper_zombie_log.csv", line)
            count = count + 1
        end
    end

    print("[DataDumper] ZombieLogger: " .. count .. " zombies logged at t=" .. ts)
end

Events.OnTickEvenHours.Add(logZombies)
