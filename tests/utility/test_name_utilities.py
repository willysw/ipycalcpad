import pytest
from ipycalcpad.utility.name_utilities import (
    name_to_tex,
)


@pytest.fixture
def basic_names():
    """Fixture providing basic variable names for testing."""
    return {
        'x': 'x',
        'y': 'y',
        'alpha': '\\alpha',
    }


@pytest.fixture
def subscripted_names():
    """Fixture providing subscripted variable names for testing."""
    return {
        'x_1': 'x_{1}',
        'x_y': 'x_{y}',
        'alpha_y': '\\alpha_{y}',
        'x_alpha': 'x_{\\alpha}',
        'alpha_alpha': '\\alpha_{\\alpha}',
    }

@pytest.fixture
def multi_subscripted_names():
    """Fixture providing multi-subscripted variable names for testing."""
    return {
        'w_1_2': 'w_{1,2}',
        'w_x_y_z': 'w_{x,y,z}',
        'alpha_x_y_z': '\\alpha_{x,y,z}',
        'w_alpha_x_y': 'w_{\\alpha,x,y}',
        'w_x_alpha_y': 'w_{x,\\alpha,y}',
        'w_x_y_alpha': 'w_{x,y,\\alpha}',
    }


@pytest.fixture
def special_name_dict():
    """Fixture providing Greek letter variable names for testing."""
    return {'alpha': '\\alpha',}


class TestNameUtilities:
    """Test cases for name_utilities module."""

    def test_module_imports(self):
        """Test that the functions in name_utilities module can be imported."""
        assert name_to_tex is not None

    def test_basic_names(self, basic_names, special_name_dict):
        """Test that basic variable names are converted to TeX correctly."""
        for name, expected_tex in basic_names.items():
            assert name_to_tex(name, special_name_dict) == expected_tex

    def test_subscripted_names(self, subscripted_names, special_name_dict):
        """Test that subscripted variable names are converted to TeX correctly."""
        for name, expected_tex in subscripted_names.items():
            assert name_to_tex(name, special_name_dict) == expected_tex

    def test_multi_subscripted_names(self, multi_subscripted_names, special_name_dict):
        """Test that multi-subscripted variable names are converted to TeX correctly."""
        for name, expected_tex in multi_subscripted_names.items():
            assert name_to_tex(name, special_name_dict) == expected_tex

    
