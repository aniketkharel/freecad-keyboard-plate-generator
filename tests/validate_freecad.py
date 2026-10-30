"""Run with FreeCAD's bundled Python from the project root."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import FreeCAD as App
from keyboard_plate.feature import create_plate
from keyboard_plate.preview import layout_preview
from keyboard_plate.kle import parse_kle

source = Path('reference/plate_generator_v0_2.FCMacro').read_text(encoding='utf-8')
reference = {'__name__': 'reference_macro'}
exec(compile(source.rsplit('\nrun()', 1)[0], 'v0.2', 'exec'), reference)
# v0.2 skips planar refinement because faces have zero volume.
# FreeCAD 1.1 needs these internal envelope seams removed before extrusion.
original_refine = reference['_refine']
def reference_refine(shape):
    return shape.removeSplitter() if not shape.Solids else original_refine(shape)
reference['_refine'] = reference_refine
data = Path('4x4_kle.json').read_text(encoding='utf-8')
for label, layout in [('sample', data), ('rotated', '[[{"rx":2,"ry":1,"r":25},"A","B"]]')]:
    doc = App.newDocument('Validation')
    old = doc.addObject('Part::FeaturePython', 'Reference')
    reference['_add_props'](old, layout)
    reference['_generate'](old)
    obj = create_plate(doc, layout)
    doc.recompute()
    assert obj.GenerationStatus.startswith('OK'), obj.GenerationStatus
    assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
    assert abs(old.Shape.Volume - obj.Shape.Volume) < 1e-6
    assert obj.Shape.cut(old.Shape).Volume < 1e-6
    assert old.Shape.cut(obj.Shape).Volume < 1e-6
    _, _, bounds = layout_preview(parse_kle(layout), 5, 14)
    box = obj.Shape.BoundBox
    assert abs(bounds[2] - bounds[0] - box.XLength) < 1e-6
    assert abs(bounds[3] - bounds[1] - box.YLength) < 1e-6
    print(label, 'volume', obj.Shape.Volume, 'bounds', box.XLength, box.YLength, box.ZLength)
    if label == 'sample':
        output = Path('validation_output')
        output.mkdir(exist_ok=True)
        filename = str((output / 'sample.FCStd').resolve())
        doc.saveAs(filename)
        App.closeDocument(doc.Name)
        doc = App.openDocument(filename)
        obj = doc.getObject('KeyboardPlate')
        assert hasattr(obj.Proxy, 'execute'), 'Proxy not restored'
        obj.OutlineMargin = 6
        obj.touch()
        doc.recompute()
        assert obj.GenerationStatus.startswith('OK'), obj.GenerationStatus
        assert abs(obj.Shape.BoundBox.XLength - 50.1) < 1e-6
        obj.ClipLipThickness = 4
        volume = obj.Shape.Volume
        doc.recompute()
        assert obj.GenerationStatus.startswith('ERROR')
        assert abs(obj.Shape.Volume - volume) < 1e-6
        print('save/reopen, editable recompute and invalid-parameter retention passed')
    App.closeDocument(doc.Name)
print('FreeCAD validation passed')
