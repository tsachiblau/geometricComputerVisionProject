function [D] = spdiag(v)
    n = length(v);
    D = spdiags(v, 0, n, n);
end
