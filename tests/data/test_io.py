from fpl.data import io

def test_io(data_dir, data_object):
    assert len(io.list_data_dir(data_dir)) == 2
    assert len(io.list_data_dir(data_dir, suffix=".gitkeep")) == 0
    assert len(io.list_data_dir(data_dir, suffix=".xlsx")) == 1
