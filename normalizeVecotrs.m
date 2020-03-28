function [norm_X] = normalizeVecotrs(X)

    norm_X = zeros(size(X));
    
    for i = 1 : size(X, 2)
        vector_i = X(:, i);
        norm_X(:, i) = vector_i / norm(vector_i);
    end
    
end

