function [W,Sc,Sl, Q] = calc_LBO_FEM_bc(M, bc)

if bc ~= "neumann" && bc ~= "dirichlet"
    disp("options for bc are dirichlet, neumann");
end

% %creat M
% M.m = 4;
% M.n = 5;
% M.indexes = 1:5;
% M.TRIV = [  [1 2 5];
%             [2 3 5];
%             [3 4 5];
%             [1 5 4]];
% M.VERT = [  [0 0 0];
%             [1 0 0];
%             [1 1 0];
%             [0 1 0];
%             [0.5 0.5 sqrt(0.5)]];


angles = zeros(M.m,3);
for i=1:3
    a = mod(i-1,3)+1;
    b = mod(i,3)+1;
    c = mod(i+1,3)+1;
    ab = M.VERT(M.TRIV(:,b),:) - M.VERT(M.TRIV(:,a),:);
    ac = M.VERT(M.TRIV(:,c),:) - M.VERT(M.TRIV(:,a),:);
    %normalize edges
    ab = ab ./ (sqrt(sum(ab.^2,2))*[1 1 1]);
    ac = ac ./ (sqrt(sum(ac.^2,2))*[1 1 1]);
    % normalize the vectors
    %for every polygons we have the angle of the vertex i at column i
    angles(:,a) = acos(sum(ab.*ac,2));
end

indicesI = [M.TRIV(:,1);M.TRIV(:,2);M.TRIV(:,3);M.TRIV(:,3);M.TRIV(:,2);M.TRIV(:,1)];
indicesJ = [M.TRIV(:,2);M.TRIV(:,3);M.TRIV(:,1);M.TRIV(:,2);M.TRIV(:,1);M.TRIV(:,3)];
values   = [angles(:,1);angles(:,2);angles(:,3);angles(:,3);angles(:,2);angles(:,1)];
Q = sparse(indicesI, indicesJ, values, M.n, M.n);
Q = sparse(1:M.n,1:M.n,abs(2*pi - sum(Q, 2)));



% Stiffness (p.s.d.)

angles = zeros(M.m,3);
for i=1:3
    a = mod(i-1,3)+1;
    b = mod(i,3)+1;
    c = mod(i+1,3)+1;
    ab = M.VERT(M.TRIV(:,b),:) - M.VERT(M.TRIV(:,a),:);
    ac = M.VERT(M.TRIV(:,c),:) - M.VERT(M.TRIV(:,a),:);
    %normalize edges
    ab = ab ./ (sqrt(sum(ab.^2,2))*[1 1 1]);
    ac = ac ./ (sqrt(sum(ac.^2,2))*[1 1 1]);
    % normalize the vectors
    % compute cotan of angles
    angles(:,a) = cot(acos(sum(ab.*ac,2)));
    %cotan can also be computed by x/sqrt(1-x^2)
end

indicesI = [M.TRIV(:,1);M.TRIV(:,2);M.TRIV(:,3);M.TRIV(:,3);M.TRIV(:,2);M.TRIV(:,1)];
indicesJ = [M.TRIV(:,2);M.TRIV(:,3);M.TRIV(:,1);M.TRIV(:,2);M.TRIV(:,1);M.TRIV(:,3)];
values   = [angles(:,3);angles(:,1);angles(:,2);angles(:,1);angles(:,3);angles(:,2)]*0.5;
W = sparse(indicesI, indicesJ, -values, M.n, M.n);
W = W-sparse(1:M.n,1:M.n,sum(W));

% Mass

%are of every tirangle, 
%size of all polygons!
areas = calc_tri_areas(M);

%building index for the sparse matrix,
%indexing of vertices!
indicesI = [M.TRIV(:,1);M.TRIV(:,2);M.TRIV(:,3);M.TRIV(:,3);M.TRIV(:,2);M.TRIV(:,1)];
indicesJ = [M.TRIV(:,2);M.TRIV(:,3);M.TRIV(:,1);M.TRIV(:,2);M.TRIV(:,1);M.TRIV(:,3)];

%
values   = [areas(:); areas(:); areas(:); areas(:); areas(:); areas(:)]./12;
Sc = sparse(indicesI, indicesJ, values, M.n, M.n);
Sc = Sc+sparse(1:M.n, 1:M.n, sum(Sc));

Sl = spdiag(sum(Sc,2));

if bc == "dirichlet"
    boundary = calc_boundary_edges(M.TRIV);
    boundary = unique(boundary(:));
    [W, Sc, Sl, Q] = dirichlet_bc(W, Sc, Sl, boundary, M.n, Q);
end

W = (W + W')/2;
Sc = (Sc + Sc')/2;

end
