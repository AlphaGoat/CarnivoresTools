vector_math = {}

function vector_math.L2dist(start_point, end_point) 
    -- Calculates the magnitude of input vector
    local sum = 0.0
    print("number in L2norm: " .. string.format("%d", start_point))
    for i, xai in ipairs(start_point) do
        xbi = end_point[i]
        sum = sum + (xai - xbi)^2
    end

    -- take sqrt and return magnitude
    mag = math.sqrt(sum)

    return mag
end


function vector_math.normalizeVector(vector)
    -- Get magnitude of vector
    mag = math.sqrt(vector[1]^2 + vector[2]^2 + vector[3]^2)
    norm_vector = {vector[1] / mag, vector[2] / mag, vector[3] / mag}
    return norm_vector
end


function vector_math.crossProduct(vectora, vectorb)
    -- (note: only works for 3-D vectors as of now...)
    -- A generalizable solution will take the determinant
    -- of the vector matrix....
    local a = { vectora[2][1] - vectora[1][1], vectora[2][2] - vectora[1][2], vectora[2][3] - vectora[1][3] }
    local b = { vectorb[2][1] - vectorb[1][1], vectorb[2][2] - vectorb[1][2], vectorb[2][3] - vectorb[1][3] }
    out_vector = {
        a[2] * b[3] - a[3] * b[2],
        a[3] * b[1] - a[1] * b[3],
        a[1] * b[2] - a[2] - b[1]
    }
    return out_vector
end


function vector_math.vectorSum(vector1, vector2) 
    sum_vector = {}
    for i, elem1 in ipairs(vector1) do
        elem2 = vector2[i]
        sum_vector[i] = elem1 + elem2
    end
    return sum_vector
end

return vector_math
