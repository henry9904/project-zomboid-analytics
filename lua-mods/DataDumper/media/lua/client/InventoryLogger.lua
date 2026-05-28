-- Snapshots the player's food inventory every 2 in-game hours, aggregated by
-- item type. Output drives the Nutrition Optimizer's decision variables.
require "DataDumper_Init"

local function safeNutri(item, getter)
    if item == nil then return 0 end
    local ok, val = pcall(function() return item[getter](item) end)
    return (ok and val) or 0
end

local function logInventory()
    local player = getSpecificPlayer(0)
    if player == nil then return end
    local inv = player:getInventory()
    if inv == nil then return end
    local items = inv:getItems()
    if items == nil then return end

    local age = getGameTime():getWorldAgeHours()
    local agg = {}
    for i = 0, items:size() - 1 do
        local it = items:get(i)
        if it ~= nil and it:IsFood() then
            local t = it:getType()
            if agg[t] == nil then
                agg[t] = {
                    count = 0,
                    cal   = safeNutri(it, "getCalories"),
                    carbs = safeNutri(it, "getCarbohydrates"),
                    prot  = safeNutri(it, "getProteins"),
                    fat   = safeNutri(it, "getLipids"),
                }
            end
            agg[t].count = agg[t].count + 1
        end
    end

    for t, v in pairs(agg) do
        local line = string.format(
            "%.3f,%s,%d,%.2f,%.2f,%.2f,%.2f",
            age, t, v.count, v.cal, v.carbs, v.prot, v.fat
        )
        DataDumper.writeLine(DataDumper.INV_LOG, line)
    end
end

Events.OnTickEvenHours.Add(logInventory)
