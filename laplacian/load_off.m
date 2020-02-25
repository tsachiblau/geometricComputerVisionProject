function shape = read_off(filename)
% read_off reads from disk a triangle mesh in .off format
%   First line is ignored
%   Second line must indicate the number of vertices and triangles
%   All the vertices are listed
%   All the triangles are listed

% dlmread starts from 0
shape = [];


vertices = load([filename, '.mat']);
shape.n = size(vertices, 1);
shape.indexes = [1:shape.n]';
shape.m = size(triangles, 1);

shape.VERT = vertices;
shape.TRIV = triangles;


end

