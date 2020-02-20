function shape = read_off(filename)
% read_off reads from disk a triangle mesh in .off format
%   First line is ignored
%   Second line must indicate the number of vertices and triangles
%   All the vertices are listed
%   All the triangles are listed

% dlmread starts from 0
offset = 1;
shape = [];

stats = dlmread(filename, ' ', [offset, 0, offset, 2]);
shape.n = stats(1);
shape.m = stats(2);
shape.indexes = [1:shape.n]';

offset = offset + 1;
vertices = dlmread(filename, ' ', [offset, 0, offset + shape.n - 1, 2]);

offset = offset + shape.n;
triangles = dlmread(filename, ' ', [offset, 0, offset + shape.m - 1, 3]);

% triangles(1);
if triangles(1) ~= 3
    error("read_off(): The mesh contains non-triangular faces")
end

shape.VERT = vertices;
shape.TRIV = triangles(: , 2:end);

% check if 0-index or 1-index
zero_present = all(shape.TRIV, 'all');
if zero_present == 0
    shape.TRIV = shape.TRIV + 1;
else
    disp('The .off file is 1-indexed');
end

end

