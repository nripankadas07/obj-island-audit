import unittest
from obj_island_audit import analyze

T='v 0 0 0\nv 1 0 0\nv 0 1 0\nv 0 0 1\nf 1 3 2\nf 1 2 4\nf 2 3 4\nf 3 1 4\n'
S='v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n'

class ObjTests(unittest.TestCase):
    def test_closed_tetra(self):
        r=analyze(T);self.assertFalse(r['has_findings']);self.assertEqual(len(r['components']),1);self.assertTrue(r['components'][0]['closed_edge_surface'])
    def test_boundary_triangle(self):
        r=analyze(S);self.assertEqual(len(r['defects']['boundary_edges']),3);self.assertAlmostEqual(r['components'][0]['area_approx'],.5)
    def test_separate_closed_islands(self):
        two=T+'v 10 0 0\nv 11 0 0\nv 10 1 0\nv 10 0 1\nf 5 7 6\nf 5 6 8\nf 6 7 8\nf 7 5 8\n'
        r=analyze(two);self.assertEqual(len(r['components']),2);self.assertFalse(r['has_findings'])
    def test_point_touch_not_edge_connection(self):
        r=analyze(S+'v -1 0 0\nv 0 -1 0\nf 1 4 5\n');self.assertEqual(len(r['components']),2);self.assertEqual(r['defects']['vertex_contacts'],[{'vertex':0,'components':[1,2]}])
    def test_exact_duplicate_vertex_weld(self):
        r=analyze(S+'v 0.0 0 0\nf 4 3 2\n');self.assertEqual(r['welded_vertices'],3);self.assertEqual(len(r['defects']['duplicate_faces']),1)
    def test_quantization_can_collapse_face(self):
        s='v 0 0 0\nv 0.0004 0 0\nv 0 1 0\nf 1 2 3\n'
        self.assertFalse(analyze(s)['defects']['degenerate_faces']);self.assertEqual(analyze(s,3)['defects']['degenerate_faces'],[1])
    def test_half_even_grid(self):
        s='v 0 0 0\nv .0005 0 0\nv 0 1 0\nf 1 2 3\n';self.assertEqual(analyze(s,3)['welded_vertices'],2)
    def test_repeated_face_is_evidence(self):
        r=analyze(S+'f 3 2 1\n');self.assertEqual(r['defects']['duplicate_faces'],[{'face':2,'same_vertices_as':1}])
    def test_collinear_degenerate(self):
        r=analyze('v 0 0 0\nv 1 0 0\nv 2 0 0\nf 1 2 3\n');self.assertEqual(r['defects']['degenerate_faces'],[1]);self.assertEqual(r['components'],[])
    def test_orientation_conflict(self):
        r=analyze(T.replace('f 1 3 2','f 1 2 3'));self.assertEqual(len(r['defects']['orientation_conflicts']),3)
    def test_nonmanifold_edge(self):
        r=analyze(S+'v 0 -1 0\nv 0 0 1\nf 2 1 4\nf 1 2 5\n');self.assertEqual(r['defects']['nonmanifold_edges'][0]['edge'],[0,1])
    def test_negative_indices_resolved_at_face(self):
        r=analyze(S.replace('f 1 2 3','f -3 -2 -1'));self.assertEqual(r['components'][0]['faces'],[1])
    def test_attribute_references(self):
        s=S.replace('f 1 2 3','vt 0 0\nvn 0 0 1\nf 1/1/1 2/1/1 3/1/1');self.assertEqual(analyze(s)['input_faces'],1)
    def test_missing_attribute_reference(self):
        with self.assertRaises(ValueError):analyze(S.replace('f 1 2 3','f 1/1 2/1 3/1'))
    def test_material_files_never_read(self):
        r=analyze('mtllib ../../missing.mtl\no example\n'+S);self.assertEqual(r['ignored_metadata'],{'mtllib':1,'o':1})
    def test_bad_faces(self):
        for face in ['f 0 2 3','f 1 2 4','f 1 2 3 1','f 1/ 2 3']:
            with self.subTest(face=face),self.assertRaises(ValueError):analyze(S.rsplit('f ',1)[0]+face)
    def test_bad_numeric_data(self):
        for n in ['nan','inf','1e99','1e-99','1000000001']:
            with self.subTest(n=n),self.assertRaises(ValueError):analyze(S.replace('v 0 0 0','v '+n+' 0 0'))
    def test_unsupported_primitives(self):
        for d in ['l 1 2','p 1','curv 0 1 1 2']:
            with self.assertRaises(ValueError):analyze(S+d)
    def test_weld_parameter(self):
        for n in [-1,10,True,1.2]:
            with self.assertRaises(ValueError):analyze(S,n)
    def test_determinism_and_unused_vertices(self):
        r=analyze(T+'v 99 99 99\n');self.assertEqual(r,analyze(T+'v 99 99 99\n'));self.assertEqual(len(r['components'][0]['vertices']),4)
    def test_connected_fan_with_many_faces(self):
        text='v 0 0 1\n'+''.join(f'v {i} {i*i} 0\n' for i in range(1,1002))+''.join(f'f 1 {i} {i+1}\n' for i in range(2,1002))
        r=analyze(text);self.assertEqual(len(r['components']),1);self.assertEqual(len(r['components'][0]['faces']),1000);self.assertEqual(r['components'][0]['boundary_edges'],1002)

if __name__=='__main__':unittest.main()
