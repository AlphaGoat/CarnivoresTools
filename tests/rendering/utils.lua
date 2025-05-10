


function encodeToAscii(inputString)
    local asciiValues = {}
    for i=1, #inputString do
        local asciiValue = string.byte(inputString, i)
        table.insert(asciiValues, asciiValue)
    end
    return asciiValues
end

function hex2bytes(str)
    -- assert that it is indeed a string of hex digit pairs
    assert(#str % 2 == 0 and not str:match"[^%x]")
    return str:gsub("%x%x", function(hex) return tonumber(hex, 16) end)
end

function bytes2uint(str)
    local uint = 0
    for i = 1, #str do
        uint = uint + str:byte(i) * 0x100^(i-1)
    end
    return uint
end


function bytes2int(str)
    local uint = bytes2uint(str)
    local max = 0x100 ^ #str
    if uint >= max / 2 then
        return uint - max
    end
    return uint
end


function sortTableByKey(input_table)
    sorted_table = {}
    
    local local_keys = {}
    for key in pairs(input_table) do
        local_keys.insert(key)
    end

    table.sort(local_keys)

    for skey in pairs(local_keys) do 
        sorted_table[skey] = input_table[skey]
    end

    return sorter_table
end


function normalize(val, min_val, max_val) 
    return 2 * ((x - min_val) / (max_val - min_val)) - 1
end


function bytesToFloat32(bin)
    local sig = string.byte(bin, 3) % 0x80 * 0x10000 + string.byte(bin, 2) * 0x100 + string.byte(bin, 1)
--    local sig = bin:byte(3) % 0x80 * 0x10000 + bin:byte(2) * 0x100 + bin:byte(1)
--    local sig = bin:byte(3) % 0x80 * 0x10000 + bin:byte(2) * 0x100 + bin:byte(1)
    local exp = string.byte(bin, 4) % 0x80 * 2 + math.floor(string.byte(bin, 3) / 0x80) - 0x7F
--    local exp = bin:byte(4) % 0x80 * 2 + math.floor(bin:byte(3) / 0x80) - 0x7F
    if exp == 0x7F then return 0 end
    return math.ldexp(math.ldexp(sig, -23) + 1, exp) * (bin:byte(4) < 0x80 and 1 or -1)
end
