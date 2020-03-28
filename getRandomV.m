function [random_v] = getRandomV(X)

    D = calcGeodesicDistances(X);
    [max_distance_sorted, I] = sort(D(:), 'descend');
    not_inf_idx = max_distance_sorted~=inf;
    max_distance_sorted_no_inf = max_distance_sorted(not_inf_idx);
    max_distance_sorted_no_inf_idx = I(not_inf_idx);
    max_distance = max_distance_sorted_no_inf(1);
    max_distance_idx = max_distance_sorted_no_inf_idx(1);
        
    D( D == inf ) = 0;
    
    seeds = [];
    [i, j] = ind2sub(size(D), max_distance_idx);
    seeds = [i j];
    num_of_seeds = 100;
    
    my_dist = max_distance / 10;
    bigger_then_D = D > my_dist;
    bigger_then_D(logical(eye(size(bigger_then_D)))) = true;
    
    for i = 3 : num_of_seeds 
        current_rows = bigger_then_D(seeds, :);
        tmp_row = current_rows(1, :);
        
        for j = 1 : size(current_rows, 1)
            tmp_row = tmp_row & current_rows(j, :);
        end
        
        new_seed = find(tmp_row);
        good_new_seeds_idx = ~ismember(new_seed, seeds);
        new_good_seeds = new_seed(good_new_seeds_idx);
        
        if isempty(new_good_seeds)
           break; 
        end
        
        seeds = [seeds, new_good_seeds(1)];
        %pick another seed
    end
    
    figure();
    patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
    hold on;
    scatter3(X.VERT(seeds(:),1), X.VERT(seeds(:),2), X.VERT(seeds(:),3), 300, 'r', 'filled');
    
    % build v for every seed
    radius_of_v = max_distance / 4;
    random_v = [];
    
        
    for i = 1 : length(seeds)
        tmp_dist = D(seeds(i), :);
        tmp_v = 1 - gaussmf(tmp_dist, [radius_of_v 0]);
        random_v = [random_v; tmp_v];
    end
    
%     f = figure();
%     for i = 1 : size(random_v, 1)
%         clf(f);
%         plot_th = 0.9;
%         tmp_row = i;
%         patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
%         hold on;
%         scatter3(X.VERT(find(random_v(tmp_row, :) < plot_th),1), X.VERT(find(random_v(tmp_row, :) < plot_th),2), X.VERT(find(random_v(tmp_row, :) < plot_th),3), 30, 'r', 'filled');
%         title(num2str(i));
%         pause(1);
%     end
%     random_v = random_v(39, :);
%     random_v = random_v(1, :);
end

