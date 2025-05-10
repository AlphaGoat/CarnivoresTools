--"""
--File parser and utilities for opening .car files
--
--Author: Peter Thomas
--Date: 31 March, 2025
--"""
require "vector_math"


function dump(o)
    if type(o) == 'table' then
        local s = '{ '
        for k, v in pairs(o) do
            if type(k) ~= 'number' then k = '"' .. k .. ':' end
            s = s .. '[' ..k.. '] = ' .. dump(v) .. ','
        end
        return s .. '} '
    else
        return tostring(o)
    end
end


function sortTableByKey(input_table)
    sorted_table = {}
    
    local local_keys = {}
    for key in pairs(input_table) do
        table.insert(local_keys, key)
    end

    table.sort(local_keys)

    for skey in pairs(local_keys) do 
        sorted_table[skey] = input_table[skey]
    end

    return sorted_table
end


function normalize(val, min_val, max_val) 
    return 2 * ((val - min_val) / (max_val - min_val)) - 1
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


-- Templates for blocks to parse from CAR file
local triangBlockMeta = {
    -- Triangle vertices (index to point object)
    Tr_Point1 = nil,
    Tr_Point2 = nil,
    Tr_Point3 = nil,

    -- coordinates of triangle vertices
    Tr_CoordX1 = nil,
    Tr_CoordX2 = nil,
    Tr_CoordX3 = nil,
    Tr_CoordY1 = nil,
    Tr_CoordY2 = nil,
    Tr_CoordY3 = nil,

    -- unknown
    Tr_U1 = nil,
    Tr_U2 = nil,

    -- index to parent triangle
    Tr_Parent = nil,

    -- also unknown
    Tr_U3 = nil,
    Tr_U4 = nil,
    Tr_U5 = nil,
    Tr_U6 = nil
}


local pointBlockMeta = {
    -- Point coordinates
    P_CoordX = nil,
    P_CoordY = nil,
    P_CoordZ = nil,

    -- Bone to which point is attached to
    P_bone = nil
}

local animationBlockMeta = {
    name = nil,
    div = nil,
    num_frames = nil,
    frames = nil
}

local frameMeta = {
    pt_coords = nil
}

local soundBlockMeta = {
    name = nil,
    length = nil,
    data = nil,
    parameters = {
        nchannels=1,
        frequency=22050
    }
}

--function bytesToString(bytes)
--    local characters = {}
--    for _, value in ipairs(bytes) do
--        local character = string.char(value)
--        table.insert(charactes, character)
--    end
--    return table.concat(characters)
--end


-- function bytesToString(bytes)
--     local decodedString = ""
--     for _, v in ipairs(bytes) do
--         decodedString = decodedString ... string.char(v)
--     end
--     return decodedString
-- end

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


CARReader = {
    filepath = "",
    header={
        name = nil,
        extra = nil,
        num_anims = nil,
        num_points = nil,
        num_triang = nil,
        bytes_tex = nil
    },
    triangles={},
    points={},
    texture=nil,
    animations={},
    sounds={},
    file=nil
}


function CARReader:new (o, filepath)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    self.filepath = filepath
--    self.header = {
--        name = nil,
--        extra = nil,
--        num_anims = nil,
--        num_points = nil,
--        num_triang = nil,
--        bytes_tex = nil
--    }
--    self.triangles = {}
--    self.points = {}
--    self.texture = nil
--    self.animations = {}
--    self.sounds = {}
--
--    -- Variable to hold file hnadle
--    self.file = nil
    return o
end

setmetatable(CARReader, {__call = CARReader.new })


function CARReader:read_file_contents()
    -- Open file
    self.file = assert(io.open(self.filepath, "rb"))

    -- Read header
    self:readHeader()

    -- Read Triangles blocks
    for i=1, self.header.num_triang do
        triblock = self:readTrianglesBlock(i)
        self.triangles[i] = triblock
    end

    -- Read in point blocks
    for j=1, self.header.num_points do
        ptblock = self:readPointBlock(j)
        self.points[j] = ptblock
    end

    -- Read in texture
    self.texture = self:readTextureBlock()

    -- Read in animations
    for k=1, self.header.num_anims do
        animblock = self:readAnimation(k)
        self.animations[k] = animblock
    end

    -- Read in sounds
    for l=1, self.header.num_sounds do
        soundblock = self:readSoundBlock(l)
        self.sounds[l] = soundblock
    end

    -- Release file handle
    self.file:close()
end


function CARReader:readHeader ()
    if (self.file == nil) then
        file = io.open(self.filepath, "rb")
        if not file then print("Failed to open file.") end
    else
        file = self.file
    end

    -- Read in dinosaur name
    local name_data = file:read(24)
--    local name = encodeToAscii(name_data)

    self.header.name = encodeToAscii(name_data) 

    -- read extra field
    local extra_data = file:read(8)
    self.header.extra = encodeToAscii(extra_data)

    -- read number of animations
    local num_anims_data = file:read(4)
    self.header.num_anims = bytes2int(num_anims_data)

    -- read number of sounds
    local num_sounds_data = file:read(4)
    self.header.num_sounds = bytes2int(num_sounds_data)

    -- number of points (vertices) in mesh
    local num_points = file:read(4)
    self.header.num_points = bytes2int(num_points)

    -- number of triangles faces in mesh
    local num_triang = file:read(4)
    self.header.num_triang = bytes2int(num_triang)

    -- Texture length in bytes
    local bytes_tex = file:read(4)
    self.header.bytes_tex = bytes2int(bytes_tex)

    -- if file was opened in this function, release handle
    if (self.file == nil) then file:close() end

end


function CARReader:readTrianglesBlock (triangBlockNum)
    -- Calculate byte offset based off which triangleBlockNum this is
    local byte_offset = 52 + (triangBlockNum - 1) * 64

    local file
    if (self.file == nil) then
        file = io.open(self.filepath, "rb")
        if not file then print("Failed to open file.") end
    else
        file = self.file
    end

    -- set file to read from offset
    file:seek("set", byte_offset)

    -- initialize triblock table to hold attributes from this file section
    triBlock = {}
    setmetatable(triBlock, triangBlockMeta)

    -- Read in triangle points
    local Tr_Point1_data = file:read(4)
    triBlock.Tr_Point1 = bytes2int(Tr_Point1_data)

    local Tr_Point2_data = file:read(4)
    triBlock.Tr_Point2 = bytes2int(Tr_Point2_data)

    local Tr_Point3_data = file:read(4)
    triBlock.Tr_Point3 = bytes2int(Tr_Point3_data)

    -- Read in cordinates of points
    local Tr_CoordX1_data = file:read(4)
    triBlock.Tr_CoordX1 = bytes2int(Tr_CoordX1_data)

    local Tr_CoordX2_data = file:read(4)
    triBlock.Tr_CoordX2 = bytes2int(Tr_CoordX2_data)

    local Tr_CoordX3_data = file:read(4)
    triBlock.Tr_CoordX3 = bytes2int(Tr_CoordX3_data)

    local Tr_CoordY1_data = file:read(4)
    triBlock.Tr_CoordY1 = bytes2int(Tr_CoordY1_data)

    local Tr_CoordY2_data = file:read(4)
    triBlock.Tr_CoordY2 = bytes2int(Tr_CoordY2_data)

    local Tr_CoordY3_data = file:read(4)
    triBlock.Tr_CoordY3 = bytes2int(Tr_CoordY3_data)

    -- Unknown data segment
    local Tr_U1_data = file:read(4)
    triBlock.Tr_U1 = bytes2int(Tr_U1_data)

    local Tr_U2_data = file:read(4)
    triBlock.Tr_U2 = bytes2int(Tr_U2_data)

    local Tr_Parent_data = file:read(4)
    triBlock.Tr_Parent = bytes2int(Tr_Parent_data)

    -- More unknown data segments
    local Tr_U3_data = file:read(4)
    triBlock.Tr_U3 = bytes2int(Tr_U3_data)

    local Tr_U4_data = file:read(4)
    triBlock.Tr_U4 = bytes2int(Tr_U4_data)

    local Tr_U5_data = file:read(4)
    triBlock.Tr_U5 = bytes2int(Tr_U5_data)

    local Tr_U6_data = file:read(4)
    triBlock.Tr_U6 = bytes2int(Tr_U6_data)

    -- if file was opened in this function, release handle
    if (self.file == nil) then file:close() end

    -- return triblock to the user
    return triBlock
end


function CARReader:readPointBlock(ptBlockNum) 
    -- Calculate byte offset based which point block number this is
    local byte_offset = 52 + self.header.num_triang * 64 + (ptBlockNum - 1) * 16

    local file
    if (self.file == nil) then
        file = io.open(self.filepath, "rb")
        if not file then print("Failed to open file.") end
    else
        file = self.file
    end

    -- set file to read from offset
    file:seek("set", byte_offset)

    -- initialize point block object to hold read in parameters
    pBlock = {}
    setmetatable(pBlock, pointBlockMeta)

    -- Read in point coordinates
    local P_CoordX_data = file:read(4)
    pBlock.P_CoordX = bytesToFloat32(P_CoordX_data)

    local P_CoordY_data = file:read(4)
    pBlock.P_CoordY = bytesToFloat32(P_CoordY_data)

    local P_CoordZ_data = file:read(4)
    pBlock.P_CoordZ = bytesToFloat32(P_CoordZ_data)

    -- Read in parent bone for point
    local P_bone_data = file:read(4)
    pBlock.P_bone = bytesToFloat32(P_bone_data)


    -- if file was opened in this function, release handle
    if (self.file == nil) then file:close() end

    -- return point block to user
    return pBlock
    
end


function CARReader:readTextureBlock()
    -- Calculate byte offset
    local byte_offset = 52 + self.header.num_triang * 64 + self.header.num_points * 16

    local file
    if (self.file == nil) then
	file = io.open(self.filepath, "rb")
	if not file then print("Failed to open file.") end
    else
        file = self.file
    end

    -- set file to read from offset
    file:seek("set", byte_offset)

    -- Initialize empty texture array to read in pixel values
    texture_array = {}
    local tex_height = math.floor(self.header.bytes_tex / (2 * 256))
    local tex_width = 256
    for i = 1, tex_height do
        texture_array[i] = {}
        for j = 1, tex_width do
            local pix_data = file:read(2)
            texture_array[i][j] = bytes2uint(pix_data)
        end
    end

    -- if file was opened in this function, release handle
    if self.file == nil then file:close() end

    -- return texture array to user
    return texture_array
end


function CARReader:readAnimation(animNum) 
    -- Calculate byte offset
    local byte_offset = 52 + self.header.num_triang * 64 + self.header.num_points * 16 + self.header.bytes_tex

    -- Check that other animations have been read in already
    -- If they haven't, read in num frames from each

    -- little extra work here, because animations can have variable number of frames
--    for i=0, #self.animations do
    for i, anim in pairs(self.animations) do
        -- add byte offsets for name, div, and num_frames parameters
        byte_offset = byte_offset + 32 + 4 + 4
--        local num_frames = self.animations[i].num_frames
        local num_frames = anim.num_frames
        local num_pts = self.header.num_points
        byte_offset = byte_offset + 2 * num_frames * (num_pts * 3)
    end

    local file
    if (self.file == nil) then
        file = io.open(self.filepath, "rb")
        if not file then print("Failed to open file.") end
    else
        file = self.file
    end

    -- set file to read from offset
    file:seek("set", byte_offset)

    -- Initialize animation table to hold parameters from file
    animation = {}
    setmetatable(animation, animationBlockMeta)

    -- Read in animation name
    local name_data = file:read(32)
    animation.name = encodeToAscii(name_data)

    -- Read in animation divisor
    local div_data = file:read(4)
    animation.div = bytes2int(div_data)

    -- Read in number of frames in animation
    local num_frames_data = file:read(4)
    animation.num_frames = bytes2int(num_frames_data)

    -- Read in all frames in block
    animation.frames = {}
    for i=1, animation.num_frames do
        -- Initialize new frame to 
        local frame = {}
        setmetatable(frame, frameMeta)
        for j=1, self.header.num_points do
            pt_coords = {}
            local pt_coord_x_data = file:read(2)
            pt_coords[1] = bytes2int(pt_coord_x_data) 

            local pt_coord_y_data = file:read(2)
            pt_coords[2] = bytes2int(pt_coord_y_data) 

            local pt_coord_z_data = file:read(2)
            pt_coords[3] = bytes2int(pt_coord_z_data) 

            frame[j] = pt_coords
        end

        -- add frame to animation table
        animation.frames[i] = frame
    end

    -- if file was opened in this function, release handle
    if self.file == nil then file:close() end

    return animation
end


function CARReader:readSoundBlock(soundNum)
    -- Calculate byte offset
    local byte_offset = 52 + self.header.num_triang * 64 + self.header.num_points * 16 + self.header.bytes_tex

    -- little extra work here, because animations can have variable number of frames
    for i=1, #self.animations do
        -- add byte offsets for name, div, and num_frames parameters
        byte_offset = byte_offset + 32 + 4 + 4
        local num_frames = self.animations[i].num_frames
        local num_pts = self.header.num_points
        byte_offset = byte_offset + 2 * num_frames * (num_pts * 3)
    end

    -- and some additional work because sounds can be variable length
    for j=1, #self.sounds do
        -- add offset for name and sounds length
        byte_offset = byte_offset + 32 + 4

        -- Add byte-length of sound
        byte_offset = byte_offset + self.sounds[j].length 
    end

    local file
    if (self.file == nil) then
        file = io.open(self.filepath, "rb")
        if not file then print("Failed to open file.") end
    else
        file = self.file
    end

    -- set file to read from offset
    file:seek("set", byte_offset)

    -- Initialize sound table to hold parameters read from file
    soundBlock = {}
    setmetatable(soundBlock, soundBlockMeta)

    -- Read in name of sound
    local name_data = file:read(32)
    soundBlock.name = encodeToAscii(name_data)

    -- Read in byte length of sound
    local length_data = file:read(4)
    soundBlock.length = bytes2int(length_data)

    -- Read in sound data
    soundBlock.data = file:read(soundBlock.length)

    if self.file == nil then file:close() end

    return soundBlock
end


function CARReader:assignUVcoordsToVertices()
    uv_coords = {}
    local texWidth = 256
    local texHeight = math.floor(self.header.bytes_tex / texWidth)
    for i, tri in pairs(self.triangles) do
        uv_coords[tri.Tr_Point1] = {tri.Tr_CoordX1 / texWidth, tri.Tr_CoordY1 / texHeight}
        uv_coords[tri.Tr_Point2] = {tri.Tr_CoordX2 / texWidth, tri.Tr_CoordY2 / texHeight}
        uv_coords[tri.Tr_Point3] = {tri.Tr_CoordX3 / texWidth, tri.Tr_CoordY3 / texHeight}
    end
    return uv_coords
end


function CARReader:getVertexArray()
    local vertex_array = {}
    local MAX_Y = 500
    local MAX_X = 500
    local MAX_Z = 500
    for i=1, self.header.num_points do
        vertex_array[i] = {
            normalize(self.points[i].P_CoordX, -MAX_X, MAX_X),
            normalize(self.points[i].P_CoordY, -MAX_Y, MAX_Y),
            normalize(self.points[i].P_CoordX, -MAX_Z, MAX_Z)
        }
    end
    return vertex_array
end


function CARReader:calcVertexNormals()
    -- Retrieve mesh vertices 
    local vertex_array = self:getVertexArray()

    -- Initialize table to store all faces whose intersection is the corresponding vertex
    local faces_to_vertices = {}

    -- Set all elements of faces array to nil to begin
    for i, vertex in ipairs(vertex_array) do
        faces_to_vertices[i] = nil
    end

    -- Get triangles and assign to vertices
    for i, tri in ipairs(self.triangles) do
        local point1 = tri.Tr_Point1
        local point2 = tri.Tr_Point2
        local point3 = tri.Tr_Point3

        local vertex1 = vertex_array[point1 + 1]
        local vertex2 = vertex_array[point2 + 1]
        local vertex3 = vertex_array[point3 + 1]

        -- Assign face to point 1
        if faces_to_vertices[point1] == nil then
            faces_to_vertices[point1] = { {vertex1, vertex2, vertex3} }
        else
            table.insert(faces_to_vertices[point1], {vertex1, vertex2, vertex3})
        end

        -- Assign face to point 2
        if faces_to_vertices[point2] == nil then
            faces_to_vertices[point2] = { {vertex1, vertex2, vertex3} }
        else
            table.insert(faces_to_vertices[point2], {vertex1, vertex2, vertex3})
        end

        -- Assign face to point 3
        if faces_to_vertices[point3] == nil then
            faces_to_vertices[point3] = { {vertex1, vertex2, vertex3} }
        else
            table.insert(faces_to_vertices[point3], {vertex1, vertex2, vertex3})
        end
    end

    -- Sort faces table by index
    local sorted_faces_to_vertices = sortTableByKey(faces_to_vertices)

    -- Calculate normals for each face intersecting a vertex and
    -- assign the mean to that vertex
    normals = {}
--    for j, faces in ipairs(sorted_faces_to_vertices) do
    for j, faces in ipairs(sorted_faces_to_vertices) do
        point_normals = {}
        for k, face in ipairs(faces) do
            -- Get edges and calculate cross product
            local edge1 = {face[1], face[2]}
            local edge2 = {face[1], face[3]}

--            local norm1 = vector_math.L2norm(edge1[1], edge1[2])
--            local norm2 = vector_math.L2norm(edge2[1], edge2[2])

            local cross_vector = vector_math.crossProduct(edge1, edge2)

            norm = vector_math.normalizeVector(cross_vector)

            table.insert(point_normals, norm)
        end

        -- Average normals
        local num_faces = #point_normals

        local sum_vector = {0.0, 0.0, 0.0}
        for l, norm in ipairs(point_normals) do
            sum_vector = vector_math.vectorSum(sum_vector, norm) 
        end

        norm = {sum_vector[1] / num_faces, sum_vector[2] / num_faces, sum_vector[3] / num_faces }
        table.insert(normals, norm)
    end

    return normals
end


function CARReader:getElementArray()
    -- Convert triangles into an element array for opengl
    element_array = {}
    for i, tri in pairs(self.triangles) do
        table.insert(element_array, {tri.Tr_Point1, tri.Tr_Point2, tri.Tr_Point3})
    end

    return element_array
end


function CARReader:getNumVertices()
    local count = 0
    local vertex_array = self:getVertexArray()
    for _ in pairs(vertex_array) do
        count = count + 1
    end
    return count
end


function CARReader:getTexture()
    return self.texture
end

--return CARReader


--filepath = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/CERATO1.CAR"
---- 
--reader = CARReader:new(nil, filepath)
--reader:read_file_contents()
--num_vertices = reader:getNumVertices()
--print("num vertices: " .. tostring(num_vertices))
--reader:assignUVcoordsToVertices()
--reader:calcVertexNormals()
--reader:getElementArray()
