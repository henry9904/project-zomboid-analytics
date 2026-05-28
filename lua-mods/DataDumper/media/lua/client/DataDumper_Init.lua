-- DataDumper: entry point and shared utilities
-- All output goes to %UserProfile%/Zomboid/Lua/

DataDumper = {}
DataDumper.FLUSH_INTERVAL = 100  -- flush every N lines
DataDumper._buffers = {}

function DataDumper.getTimestamp()
    local gt = getGameTime()
    return string.format("%.2f", gt:getWorldAgeHours())
end

function DataDumper.writeCSVLine(filename, line)
    local writer = getFileWriter(filename, true, false)
    writer:write(line .. "\n")
    writer:close()
end

function DataDumper.writeHeader(filename, header)
    -- Write header only if file is new (check by trying to read first line)
    local reader = getFileReader(filename, false)
    if reader == nil then
        DataDumper.writeCSVLine(filename, header)
    else
        reader:close()
    end
end

Events.OnGameStart.Add(function()
    DataDumper.writeHeader(
        "datadumper_player_stats.csv",
        "world_age_hours,day,hour,x,y,z,hunger,thirst,fatigue,stress,panic,boredom,calories,weight,carbs,protein,fat"
    )
    DataDumper.writeHeader(
        "datadumper_zombie_log.csv",
        "world_age_hours,zx,zy,zz,state"
    )
    DataDumper.writeHeader(
        "datadumper_noise_events.csv",
        "world_age_hours,src_x,src_y,volume"
    )
    print("[DataDumper] Initialized. Output: %UserProfile%/Zomboid/Lua/")
end)
