function [Y] = getPartialShape(X, num_of_polygons, seed_num)
    rng(seed_num);
    remaining_polygon_list = 1 : X.m;

    taken_polygon_list = [int16(rand() * X.m)];
    
    remaining_polygon_list = remaining_polygon_list(~ismember(remaining_polygon_list, taken_polygon_list));
    
    vertics_list = [X.TRIV(taken_polygon_list, :)]';
    
    
    while size(taken_polygon_list, 2) < taken_polygon_list
        relevant_polygons = sum( ismember(X.TRIV(remaining_polygon_list, :), vertics_list), 2);
        [B, I] = sort(relevant_polygons, 'descend');
        neighbors = B >= 2;
        taken_polygon_list = [taken_polygon_list, remaining_polygon_list(I(neighbors))];
        vertex_to_add = X.TRIV( remaining_polygon_list(I(neighbors)), :);
        vertics_list = cat(1, vertics_list, vertex_to_add(:));

        remaining_polygon_list = remaining_polygon_list(~ismember(remaining_polygon_list, taken_polygon_list));
        
    end
    
    Y.n = X.n;
    Y.m = size(taken_polygon_list, 2);
    Y.indexes = 1 : size(taken_polygon_list, 2);
    Y.VERT = X.VERT;
    Y.TRIV = X.TRIV(taken_polygon_list, :);
    
end

