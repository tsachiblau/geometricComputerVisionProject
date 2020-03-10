function [alpha] = updateAlpha(error_list, alpha)
    
    size_of_samples = size(error_list, 2);
    number_of_batch = 5;
    mean_of_last = meanOfSub(error_list, size_of_samples, number_of_batch);
    mean_of_last_last = meanOfSub(error_list, size_of_samples - number_of_batch, number_of_batch);

    % if the last mean of sub is smaller its better
    if error_list(end) > error_list(end-number_of_batch) |...
            ~all(getSub(error_list, size_of_samples, number_of_batch) <= 0)
        alpha = alpha / 4;
    
    elseif mean_of_last >= mean_of_last_last
        alpha = alpha * 2;
    end
    
    if alpha > 1e10
        alpha = 1e10;
    elseif alpha < 1e-4
        alpha = 1e-4
    end
end


function [alpha] = meanOfSub(error_list, size_of_samples, number_of_batch)
    first_sub = getSub(error_list, size_of_samples, number_of_batch);
    alpha = mean(first_sub);
end

function [first_sub] = getSub(error_list, size_of_samples, number_of_batch)
    first = error_list(size_of_samples - number_of_batch + 1: size_of_samples);
    seccond = error_list(size_of_samples - number_of_batch : size_of_samples - 1);    
    first_sub = first - seccond;
end
