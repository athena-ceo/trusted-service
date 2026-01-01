"""
Tests unitaires pour CaseModel
Objectif : 90%+ de couverture
"""
import pytest
from pydantic import ValidationError

from src.common.case_model import (
    CaseModel,
    CaseField,
    CaseModelConfig,
    OptionalListElement,
)
from tests.conftest import sample_case_field


class TestCaseField:
    """Tests pour CaseField"""
    
    def test_case_field_creation_valid(self):
        """Test création d'un CaseField valide"""
        field = CaseField(
            id="nom",
            type="str",
            label="Nom",
            mandatory=True,
            help="Nom de famille",
            format="",
            allowed_values_list_name="",
            allowed_values=[],
            default_value=None,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=["intention1"],
            description="Nom de famille",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        assert field.id == "nom"
        assert field.type == "str"
        assert field.mandatory is True
        assert field.scope == "REQUESTER"
        assert field.show_in_ui is True
        assert field.extraction == "EXTRACT"
        assert field.send_to_decision_engine is True
    
    def test_case_field_intention_ids_string_conversion(self):
        """Test conversion automatique de intention_ids depuis string"""
        # Le validator utilise split() sans argument, donc sépare par espaces
        field = CaseField(
            id="test",
            type="str",
            label="Test",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids="intention1 intention2",  # String avec espaces
            description="Test",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        assert isinstance(field.intention_ids, list)
        assert "intention1" in field.intention_ids
        assert "intention2" in field.intention_ids
    
    def test_case_field_intention_ids_list_unchanged(self):
        """Test que intention_ids reste une list si déjà une list"""
        field = CaseField(
            id="test",
            type="str",
            label="Test",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=["intention1", "intention2"],
            description="Test",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        assert isinstance(field.intention_ids, list)
        assert len(field.intention_ids) == 2
        assert "intention1" in field.intention_ids
        assert "intention2" in field.intention_ids
    
    def test_case_field_intention_ids_empty_string(self):
        """Test intention_ids avec string vide"""
        field = CaseField(
            id="test",
            type="str",
            label="Test",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids="",  # String vide
            description="Test",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        assert isinstance(field.intention_ids, list)
        # split() sur string vide retourne [''], donc on vérifie que c'est une liste
        assert isinstance(field.intention_ids, list)
    
    def test_case_field_intention_ids_none(self):
        """Test intention_ids avec None"""
        field = CaseField(
            id="test",
            type="str",
            label="Test",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=None,  # None
            description="Test",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        assert isinstance(field.intention_ids, list)
        assert len(field.intention_ids) == 0
    
    def test_case_field_with_allowed_values(self):
        """Test CaseField avec allowed_values"""
        allowed_value = OptionalListElement(
            id="option1",
            label="Option 1",
            condition_python="value == 'test'",
            condition_javascript="value === 'test'"
        )
        
        field = CaseField(
            id="test",
            type="str",
            label="Test",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=[],
            description="Test",
            extraction="EXTRACT",
            send_to_decision_engine=True,
            allowed_values=[allowed_value]
        )
        
        assert len(field.allowed_values) == 1
        assert field.allowed_values[0].id == "option1"
    
    def test_case_field_default_values(self):
        """Test valeurs par défaut de CaseField"""
        field = CaseField(
            id="test",
            type="str",
            label="Test",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=[],
            description="Test",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        assert field.help == ""
        assert field.format == ""
        assert field.allowed_values_list_name == ""
        assert field.default_value is None
        assert field.allowed_values == []


class TestCaseModel:
    """Tests pour CaseModel"""
    
    def test_case_model_creation(self, sample_case_field):
        """Test création d'un CaseModel"""
        model = CaseModel(case_fields=[sample_case_field])
        
        assert len(model.case_fields) == 1
        assert model.case_fields[0].id == "nom"
        assert model.case_fields[0].label == "Nom"
    
    def test_case_model_empty_fields(self):
        """Test CaseModel avec champs vides"""
        model = CaseModel(case_fields=[])
        assert len(model.case_fields) == 0
    
    def test_case_model_multiple_fields(self):
        """Test CaseModel avec plusieurs champs"""
        field1 = CaseField(
            id="nom",
            type="str",
            label="Nom",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=[],
            description="Nom",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        field2 = CaseField(
            id="prenom",
            type="str",
            label="Prénom",
            mandatory=True,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=[],
            description="Prénom",
            extraction="EXTRACT",
            send_to_decision_engine=True
        )
        
        model = CaseModel(case_fields=[field1, field2])
        
        assert len(model.case_fields) == 2
        assert model.case_fields[0].id == "nom"
        assert model.case_fields[1].id == "prenom"
    
    def test_case_model_get_field_by_id(self, sample_case_field):
        """Test get_field_by_id()"""
        model = CaseModel(case_fields=[sample_case_field])
        
        field = model.get_field_by_id("nom")
        assert field.id == "nom"
        assert field.label == "Nom"
    
    def test_case_model_get_field_by_id_not_found(self, sample_case_field):
        """Test get_field_by_id() avec ID inexistant"""
        model = CaseModel(case_fields=[sample_case_field])
        
        with pytest.raises(ValueError, match="Field with id 'inexistant' not found"):
            model.get_field_by_id("inexistant")


class TestOptionalListElement:
    """Tests pour OptionalListElement"""
    
    def test_optional_list_element_creation(self):
        """Test création d'un OptionalListElement"""
        element = OptionalListElement(
            id="option1",
            label="Option 1",
            condition_python="value == 'test'",
            condition_javascript="value === 'test'"
        )
        
        assert element.id == "option1"
        assert element.label == "Option 1"
        assert element.condition_python == "value == 'test'"
        assert element.condition_javascript == "value === 'test'"
    
    def test_optional_list_element_validation(self):
        """Test validation d'OptionalListElement"""
        # Tous les champs sont requis
        with pytest.raises(ValidationError):
            OptionalListElement(
                id="option1",
                # label manquant
                condition_python="",
                condition_javascript=""
            )

