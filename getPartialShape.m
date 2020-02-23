function [Y] = getPartialShape(X, num_of_polygons, seed_num)
    
    rng(seed_num);
    remaining_polygon_list = 1 : X.m;
    taken_polygon_list = [int16(rand() * X.m)];
    remaining_polygon_list = remaining_polygon_list(~ismember(remaining_polygon_list, taken_polygon_list));
    vertics_list = [X.TRIV(taken_polygon_list, :)]';
    
    while size(taken_polygon_list, 2) < num_of_polygons
        relevant_polygons = sum( ismember(X.TRIV(remaining_polygon_list, :), vertics_list), 2);
        [B, I] = sort(relevant_polygons, 'descend');
        neighbors = B >= 2;
        taken_polygon_list = [taken_polygon_list, remaining_polygon_list(I(neighbors))];
        vertex_to_add = X.TRIV( remaining_polygon_list(I(neighbors)), :);
        vertics_list = cat(1, vertics_list, vertex_to_add(:));
        remaining_polygon_list = remaining_polygon_list(~ismember(remaining_polygon_list, taken_polygon_list));
    end
    
    relevant_polygons = sum( ismember(X.TRIV(remaining_polygon_list, :), vertics_list), 2);
    [B, I] = sort(relevant_polygons, 'descend');
    neighbors = B >= 3;
    taken_polygon_list = [taken_polygon_list, remaining_polygon_list(I(neighbors))];
    vertex_to_add = X.TRIV( remaining_polygon_list(I(neighbors)), :);
    vertics_list = cat(1, vertics_list, vertex_to_add(:));
    remaining_polygon_list = remaining_polygon_list(~ismember(remaining_polygon_list, taken_polygon_list));

    
    %remove polygons that have vertices that he is share with only one
    %polygon
    relevant_polygons = X.TRIV(taken_polygon_list, :);
    all_vertices = sort(unique(relevant_polygons));
    
    remove_polygons = [];
    remove_points = [];
    
    for i = 1:size(all_vertices, 1)
        tmp_sum = sum(sum(X.TRIV(taken_polygon_list, :) == all_vertices(i)));
        if tmp_sum == 1
            tmp_idx = find(sum(X.TRIV(taken_polygon_list, :) == all_vertices(i), 2));
            remove_polygons = [remove_polygons, tmp_idx];
            remove_points = [remove_points, all_vertices(i)];
        end
    end
    
    taken_polygon_list = taken_polygon_list(~ismember(1:size(taken_polygon_list, 2), remove_polygons));
    vertics_list = vertics_list(~ismember(vertics_list, remove_points));
    
    tmp = X.TRIV(taken_polygon_list, :);
    new_TRIV = [];
    idx_of_vertex_in_original_array = sort(unique(vertics_list));
    
    for i = 1 : size(taken_polygon_list, 2)
        new_row = [];
        for j = 1 : 3
            convert_idx = find(idx_of_vertex_in_original_array == tmp(i, j));
            new_row = [new_row, convert_idx];
        end
        new_TRIV = [new_TRIV; new_row];
    end
            
    Y.n = size(idx_of_vertex_in_original_array, 1);
    Y.m = size(taken_polygon_list, 2);
    Y.indexes = 1 : size(taken_polygon_list, 2);
    Y.VERT = X.VERT(idx_of_vertex_in_original_array, :);
    Y.TRIV = new_TRIV;
    
    Y.ORIGINAL_VERT = X.VERT;
    Y.ORIGINAL_TRIV = X.TRIV(taken_polygon_list, :);
    
end

