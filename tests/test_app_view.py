import pytest
from page_analyzer.utility_function import datas_to_dict


@pytest.fixture()
def get_dict_from_select():
    datas = {'column_name': ('id', 'name'), 'rows': (('1', 'name1'), ('2', 'name2'))}
    result = ({'id': '1', 'name': 'name1'}, {'id': '2', 'name': 'name2'})
    return datas, result


def test_get_dict_from_select(get_dict_from_select):
    datas, result = get_dict_from_select
    assert datas_to_dict(datas) == result
