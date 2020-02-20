function [W, A, AL] = dirichlet_bc(W_full, A_full, AL_full, boundary, n)
boundary = unique(boundary(:));
l = size(boundary,1);
inside = setdiff(1:n, boundary);
W = sparse(n, n);
W(boundary, boundary) = eye(l);
W(inside, inside) = W_full(inside, inside);
A = sparse(n, n);
A(inside,inside) = A_full(inside, inside);
AL = sparse(n, n);
AL(inside,inside) = AL_full(inside, inside);
end