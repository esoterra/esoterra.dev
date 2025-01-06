# Copyright (C) 2025 Robin Brown
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import reduce
from typing import NamedTuple, List, Optional

class Bounds(NamedTuple):
    min_x: int
    min_y: int
    max_x: int
    max_y: int

def merge_bounds(left, right) -> Bounds:
    return Bounds(
        min_x=min(left.min_x, right.min_x),
        min_y=min(left.min_y, right.min_y),
        max_x=max(left.max_x, right.max_x),
        max_y=max(left.max_y, right.max_y))

class Point(NamedTuple):
    x: int
    y: int

class Transform(NamedTuple):
    x_scale: int
    x_offset: int
    y_scale: int
    y_offset: int

    def apply(self, point: Point) -> Point:
        x = self.x_offset + self.x_scale*point.x
        y = self.y_offset + self.y_scale*point.y
        return Point(x, y)
    
    def apply_to_distance(self, dist: float):
        if abs(self.x_scale) != abs(self.y_scale):
            raise ValueError("Can't scale distances if X and Y scale don't have same magnitude")
        return dist*abs(self.x_scale)

class Text(NamedTuple):
    point: Point
    text: str
    baseline: Optional[str]
    anchor: Optional[str]

    def bounds(self) -> Bounds:
        return Bounds(self.point.x, self.point.y, self.point.x, self.point.y)

    def render(self, transform) -> str:
        point = transform.apply(self.point)
        attributes = " ".join(self.attributes(point))
        return f"<text {attributes}>{self.text}</text>"

    def attributes(self, point):
        yield f"x=\"{point.x}\""
        yield f"y=\"{point.y}\""
        if self.baseline is not None:
            yield f"dominant-baseline=\"{self.baseline}\""
        if self.anchor is not None:
            yield f"text-anchor=\"{self.anchor}\""


class PolyLine(NamedTuple):
    stroke: str
    dashed: bool
    width: int
    data: List[Point]

    def bounds(self) -> Bounds:
        min_x = min(point.x for point in self.data)
        min_y = min(point.y for point in self.data)
        max_x = max(point.x for point in self.data)
        max_y = max(point.y for point in self.data)
        return Bounds(min_x, min_y, max_x, max_y)

    def render(self, transform: Transform) -> str:
        transformed_points = [transform.apply(point) for point in self.data]
        points = " ".join(f"{point.x},{point.y}" for point in transformed_points)
        attributes = " ".join(self.attributes(points))
        return f"<polyline {attributes}/>"

    def attributes(self, points):
        yield "fill=\"none\""
        yield f"stroke=\"{self.stroke}\""
        if self.dashed:
            yield f"stroke-dasharray=\"5,5\""
        yield f"stroke-width=\"{self.width}\""
        yield f"points=\"{points}\""

class Circle(NamedTuple):
    point: Point
    radius: float
    stroke: Optional[str]
    width: Optional[int]
    fill: Optional[str]

    def bounds(self) -> Bounds:
        min_x = self.point.x - self.radius
        min_y = self.point.y - self.radius
        max_x = self.point.x + self.radius
        max_y = self.point.y + self.radius
        return Bounds(min_x, min_y, max_x, max_y)

    def render(self, transform: Transform) -> str:
        point = transform.apply(self.point)
        radius = transform.apply_to_distance(self.radius)
        attributes = " ".join(self.attributes(point, radius))
        return f"<circle {attributes}/>"

    def attributes(self, point, radius):
        yield f"cx=\"{point.x}\""
        yield f"cy=\"{point.y}\""
        yield f"r=\"{radius}\""

        if self.stroke is not None:
            yield f"stroke=\"{self.stroke}\""
            yield f"stroke-width=\"{self.width}\""

        if self.fill is None:
            yield "fill=\"none\""
        else:
            yield f"fill=\"{self.fill}\""


class Chart(NamedTuple):
    margin: int
    scale: int
    contents: List['PolyLine']

    def __repr__(self):
        bounds = reduce(merge_bounds, (line.bounds() for line in self.contents))
        transform = Transform(
            x_offset=self.margin-(bounds.min_x*self.scale),
            x_scale=self.scale,
            y_offset=self.margin+(bounds.max_y*self.scale),
            y_scale=-self.scale)
        rendered_contents = "".join(line.render(transform) for line in self.contents)
        width = 2*self.margin + (bounds.max_x - bounds.min_x)*self.scale
        height = 2*self.margin + (bounds.max_y - bounds.min_y)*self.scale
        return f"<svg viewbox=\"0 0 {width} {height}\" width=\"400px\">{rendered_contents}</svg>"

contents = []
# Vertical guides
contents.append(PolyLine("#6D606F", True, 2, [Point(1,0), Point(1,25)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(12,0), Point(12,25)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(13,0), Point(13,25)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(24,0), Point(24,25)]))

# Horizontal guides
contents.append(PolyLine("#6D606F", True, 2, [Point(0,1), Point(24,1)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,12), Point(24,12)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,13), Point(24,13)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,24), Point(24,24)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,25), Point(24,25)]))

# Diagonal guides
contents.append(PolyLine("#6D606F", True, 2, [Point(0,0), Point(24,24)]))

# Y-Axis Markers
for i in reversed(range(0,25)):
    contents.append(Text(Point(-1, i), str(i), "middle", "middle"))

# X-Axis Markers
contents.append(Text(Point(0, -1), "12", None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i, -1), str(i), None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i+12, -1), str(i), None, "middle"))

contents.append(PolyLine("#BA5624", False, 2, [Point(0, -1.5), Point(0, -2), Point(4.5, -2)]))
contents.append(PolyLine("#BA5624", False, 2, [Point(6.5, -2), Point(11, -2), Point(11, -1.5)]))
contents.append(Text(Point(5.5, -2), "a.m.", "middle", "middle"))

contents.append(PolyLine("#BA5624", False, 2, [Point(12, -1.5), Point(12, -2), Point(16.5, -2)]))
contents.append(PolyLine("#BA5624", False, 2, [Point(18.5, -2), Point(23, -2), Point(23, -1.5)]))
contents.append(Text(Point(17.5, -2), "p.m.", "middle", "middle"))

contents.append(Text(Point(24, -2), "a.m.", "middle", "middle"))

# Axis
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(24,0)]))
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(0,25)]))
# Data
contents.append(PolyLine("#BA5624", False, 4, [Point(0,12), Point(1,13)]))
contents.append(Circle(Point(0, 12), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(1, 13), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(PolyLine("#BA5624", False, 4, [Point(1,1), Point(12,12)]))
contents.append(Circle(Point(1, 1), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(12, 12), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(PolyLine("#BA5624", False, 4, [Point(12,24), Point(13,25)]))
contents.append(Circle(Point(12, 24), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(13, 25), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(PolyLine("#BA5624", False, 4, [Point(13,13), Point(24,24)]))
contents.append(Circle(Point(13, 13), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(24, 24), 0.25, "#BA5624", 4, "#FFFFFF"))

print("Figure 1:")
print()
print(Chart(25, 25, contents))
print()

# ***********************************************************************************************************************
# ***********************************************************************************************************************

contents = []
# Vertical guides
contents.append(PolyLine("#6D606F", True, 2, [Point(1,0), Point(1,25)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(24,0), Point(24,25)]))

# Horizontal guides
contents.append(PolyLine("#6D606F", True, 2, [Point(0,1), Point(24,1)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,24), Point(24,24)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,25), Point(24,25)]))

# Y-Axis Markers
for i in reversed(range(0,25)):
    contents.append(Text(Point(-1, i), str(i), "middle", "middle"))

# X-Axis Markers
contents.append(Text(Point(0, -1), "12", None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i, -1), str(i), None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i+12, -1), str(i), None, "middle"))

contents.append(Text(Point(0, -2), "p.m.", "middle", "middle"))

contents.append(PolyLine("#BA5624", False, 2, [Point(1, -1.5), Point(1, -2), Point(5.5, -2)]))
contents.append(PolyLine("#BA5624", False, 2, [Point(7.5, -2), Point(12, -2), Point(12, -1.5)]))
contents.append(Text(Point(6.5, -2), "a.m.", "middle", "middle"))

contents.append(PolyLine("#BA5624", False, 2, [Point(13, -1.5), Point(13, -2), Point(17.5, -2)]))
contents.append(PolyLine("#BA5624", False, 2, [Point(19.5, -2), Point(24, -2), Point(24, -1.5)]))
contents.append(Text(Point(18.5, -2), "p.m.", "middle", "middle"))

# Axis
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(24,0)]))
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(0,25)]))
# Data
contents.append(PolyLine("#BA5624", False, 4, [Point(0,24), Point(1,25)]))
contents.append(Circle(Point(0, 24), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(1, 25), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(PolyLine("#BA5624", False, 4, [Point(1,1), Point(24,24)]))
contents.append(Circle(Point(1, 1), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(24, 24), 0.25, "#BA5624", 4, "#FFFFFF"))

print("Figure 2:")
print()
print(Chart(25, 25, contents))
print()

# ***********************************************************************************************************************
# ***********************************************************************************************************************

contents = []
# Vertical guides
contents.append(PolyLine("#6D606F", True, 2, [Point(1,0), Point(1,13)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(13,0), Point(13,13)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(24,0), Point(24,13)]))

# Horizontal guides
contents.append(PolyLine("#6D606F", True, 2, [Point(0,1), Point(24,1)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,12), Point(24,12)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(0,13), Point(24,13)]))

# Y-Axis Markers
for i in reversed(range(0,13)):
    contents.append(Text(Point(-1, i), str(i), "middle", "middle"))

# X-Axis Markers
contents.append(Text(Point(0, -1), "12", None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i, -1), str(i), None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i+12, -1), str(i), None, "middle"))

# Axis
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(24,0)]))
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(0,13)]))
# Data
contents.append(PolyLine("#BA5624", False, 4, [Point(0,12), Point(1,13)]))
contents.append(Circle(Point(0, 12), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(1, 13), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(PolyLine("#BA5624", False, 4, [Point(1,1), Point(13,13)]))
contents.append(Circle(Point(1, 1), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(13, 13), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(PolyLine("#BA5624", False, 4, [Point(13,1), Point(24,12)]))
contents.append(Circle(Point(13, 1), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(24, 12), 0.25, "#BA5624", 4, "#BA5624"))

print("Figure 3:")
print()
print(Chart(25, 25, contents))
print()

# ***********************************************************************************************************************
# ***********************************************************************************************************************

contents = []
# Vertical guides
contents.append(PolyLine("#6D606F", True, 2, [Point(12,0), Point(12,12)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(24,0), Point(24,12)]))

# Horizontal guides
contents.append(PolyLine("#6D606F", True, 2, [Point(0,12), Point(24,12)]))

# Y-Axis Markers
for i in reversed(range(0,13)):
    contents.append(Text(Point(-1, i), str(i), "middle", "middle"))

# X-Axis Markers
contents.append(Text(Point(0, -1), "12", None, "middle"))
for i in range(0,13):
    contents.append(Text(Point(i, -1), str(12-i), None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i+12, -1), str(i), None, "middle"))

# Axis
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(24,0)]))
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(0,12)]))
# Data
contents.append(PolyLine("#BA5624", False, 4, [Point(0,12), Point(12,0)]))
contents.append(PolyLine("#BA5624", False, 4, [Point(12,0), Point(24,12)]))
contents.append(Circle(Point(0, 12), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(Circle(Point(12, 0), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(24, 12), 0.25, "#BA5624", 4, "#BA5624"))

print("Figure 4:")
print()
print(Chart(25, 25, contents))
print()

# ***********************************************************************************************************************
# ***********************************************************************************************************************

contents = []
# Vertical guides
contents.append(PolyLine("#6D606F", True, 2, [Point(12,0), Point(12,12)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(24,0), Point(24,12)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(36,0), Point(36,12)]))
contents.append(PolyLine("#6D606F", True, 2, [Point(48,0), Point(48,12)]))

# Horizontal guides
contents.append(PolyLine("#6D606F", True, 2, [Point(0,12), Point(48,12)]))

# Y-Axis Markers
for i in reversed(range(0,13)):
    contents.append(Text(Point(-1, i), str(i), "middle", "middle"))

# X-Axis Markers
contents.append(Text(Point(0, -1), "12", None, "middle"))
for i in range(0,13):
    contents.append(Text(Point(i, -1), str(12-i), None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i+12, -1), str(i), None, "middle"))
for i in range(0,13):
    contents.append(Text(Point(i+24, -1), str(12-i), None, "middle"))
for i in range(1,13):
    contents.append(Text(Point(i+36, -1), str(i), None, "middle"))

# Axis
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(48,0)]))
contents.append(PolyLine("#000", False, 4, [Point(0,0), Point(0,12)]))
# Data
contents.append(PolyLine("#BA5624", False, 4, [Point(0,12), Point(12,0)]))
contents.append(PolyLine("#BA5624", False, 4, [Point(12,0), Point(24,12)]))
contents.append(PolyLine("#BA5624", False, 4, [Point(24,12), Point(36,0)]))
contents.append(PolyLine("#BA5624", False, 4, [Point(36,0), Point(48,12)]))
contents.append(Circle(Point(0, 12), 0.25, "#BA5624", 4, "#FFFFFF"))
contents.append(Circle(Point(12, 0), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(24, 12), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(36, 0), 0.25, "#BA5624", 4, "#BA5624"))
contents.append(Circle(Point(48, 12), 0.25, "#BA5624", 4, "#BA5624"))

print("Figure 5:")
print()
print(Chart(25, 25, contents))
print()