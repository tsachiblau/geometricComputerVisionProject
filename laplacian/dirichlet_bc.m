function [W, A, AL, Q] = dirichlet_bc(W_full, A_full, AL_full, boundary, n, Q_full)

    l = size(boundary,1);
    inside = setdiff(1:n, boundary);
    
    %set W
    W = sparse(n, n);
    W(boundary, boundary) = eye(l);
    W(inside, inside) = W_full(inside, inside);
    
    %set A
    A = sparse(n, n);
    A(inside,inside) = A_full(inside, inside);
    
    %set AL
    AL = sparse(n, n);
    AL(inside,inside) = AL_full(inside, inside);

    if ~isnan(Q_full)
        Q = sparse(n, n);
        Q(inside,inside) = Q_full(inside, inside);
    else
        Q = nan;
    end
    
end