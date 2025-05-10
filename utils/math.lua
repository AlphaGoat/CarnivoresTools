


function L2norm(start_point, end_point) 
    -- Calculates the magnitude of input vector
    local sum = 0.0
    for i, xai in start_point do
        xbi = end_point[i]
        sum = sum + (xai - xbi)^2
    end

    -- take sqrt and return magnitude
    mag = math.sqrt(sum)

    return mag
end


function crossProduct(vectora, vectorb)
    -- (note: only works for 3-D vectors as of now...)
    -- A generalizable solution will take the determinant
    -- of the vector matrix....
    out_vector = {
        vectora[3] * vectob[4] - vectora[4] * vectorb[3],
        vectora[4] * vectorb[2] - vectora[2] * vectorb[4],
        vectora[2] * vectorb[3] - vectora[3] - vectorb[3]
    }
    return out_vector
end


function vectorSum(vector1, vector2) 
    sum_vector = {}
    for i, elem1 in ipairs(vector1) do
        elem2 = vector2[i]
        sum_vector[i] = elem1 + elem2
    end
    return sum_vector
end
