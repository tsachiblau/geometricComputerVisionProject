function [random_v] = getRandomV(X)

    D = calcGeodesicDistances(X);
    [max_distance, I] = sort(D(:), 'descend');
    not_inf_idx = max_distance~=inf;
    max_distance = max_distance(not_inf_idx);
    max_distance_idx = I(not_inf_idx);
    max_distance = max_distance(1);
    max_distance_idx = max_distance_idx(1);
    
    [i, j] = ind2sub(size(D), I(~not_inf_idx));
    for row = 1 : length(i)
       D(i(row),j(row)) = 0; 
    end
    
    seeds = [];
    [i, j] = ind2sub(size(D), max_distance_idx);
    seeds = [i j];
    num_of_seeds = 20;
    
    my_dist = max_distance / 6;
    my_D = D > my_dist;
    my_D(logical(eye(size(D)))) = true;
    
    for i = 3 : num_of_seeds 
        current_rows = my_D(seeds, :);
        tmp_row = current_rows(1, :);
        
        for j = 1 : size(current_rows, 1)
            tmp_row = tmp_row & current_rows(j, :);
        end
        new_seed = find(tmp_row);
        good_new_seeds_idx = ~ismember(new_seed, seeds);
        new_good_seeds = new_seed(good_new_seeds_idx);
        seeds = [seeds, new_good_seeds(1)];
        %pick another seed
    end
    
    figure();
    patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
    hold on;
    scatter3(X.VERT(seeds(:),1), X.VERT(seeds(:),2), X.VERT(seeds(:),3), 300, 'r', 'filled');
    
    % build v fpr every seed
    radius_of_v = max_distance / 4;
    random_v = [];
    for i = 1 : num_of_seeds
        tmp_v = D(seeds(i), :) > radius_of_v;
        random_v = [random_v; tmp_v];
    end
    
    tmp_row = 1;
    figure();
    patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
    hold on;
    scatter3(X.VERT(find(random_v(tmp_row, :)),1), X.VERT(find(random_v(tmp_row, :)),2), X.VERT(find(random_v(tmp_row, :)),3), 30, 'r', 'filled');
    random_v = random_v(1, :);
    
end

