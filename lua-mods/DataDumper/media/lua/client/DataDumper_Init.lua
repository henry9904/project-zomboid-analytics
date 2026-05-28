-- DataDumper init: shared file-writer utility + one-shot header bootstrap.
-- All loggers in this directory require this module first.

DataDumper = DataDumper or {}
DataDumper.SESSION_ID  = tostring(os.time())
DataDumper.PLAYER_LOG  = "player_stats_session_"       .. DataDumper.SESSION_ID .. ".csv"
DataDumper.ZOMBIE_LOG  = "zombie_log_session_"         .. DataDumper.SESSION_ID .. ".csv"
DataDumper.NOISE_LOG   = "noise_events_session_"       .. DataDumper.SESSION_ID .. ".csv"
DataDumper.INV_LOG     = "inventory_snapshot_session_" .. DataDumper.SESSION_ID .. ".csv"

local function writeLine(filename, line)
    local w = getFileWriter(filename, true, true)
    w:write(line .. "\n")
    w:close()
end
DataDumper.writeLine = writeLine

local function initFile(filename, header)
    local r = getFileReader(filename, false)
    if r == nil then
        local w = getFileWriter(filename, true, true)
        w:write(header .. "\n")
        w:close()
    else
        r:close()
    end
end

local function onGameStart()
    initFile(DataDumper.PLAYER_LOG,
        "world_age_hours,day,hour,x,y,z,hunger,thirst,fatigue,stress,panic,boredom,calories,weight,carbs,protein,fat")
    initFile(DataDumper.ZOMBIE_LOG,
        "world_age_hours,zx,zy,zz,state")
    initFile(DataDumper.NOISE_LOG,
        "world_age_hours,source_x,source_y,intensity,noise_type")
    initFile(DataDumper.INV_LOG,
        "world_age_hours,item_type,count,calories_per_unit,carbs_per_unit,protein_per_unit,fat_per_unit")
    print("[DataDumper] session " .. DataDumper.SESSION_ID .. " logging started")
end

Events.OnGameStart.Add(onGameStart)
