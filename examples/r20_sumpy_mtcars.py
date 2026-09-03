from sumdata import dataset;
from sumplot import AesSpec, LayerSpec, PlotSpec, to_chart_spec;
mtcars=dataset("mtcars");
plot=PlotSpec(mtcars,AesSpec.from_dict({"x":"cyl","y":"mpg"}),(LayerSpec("bar3d"),));
print(to_chart_spec(plot).to_json(indent=2));
