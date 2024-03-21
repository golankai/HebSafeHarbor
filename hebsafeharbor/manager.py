from typing import Dict, Optional, List

from hebsafeharbor import Doc
from hebsafeharbor.anonymizer.phi_anonymizer import PhiAnonymizer
from hebsafeharbor.identifier.phi_identifier import PhiIdentifier

class HebSafeHarbor:
    """
    The manager of the application. When it called, given a Hebrew text, it executes the identification and
    anonymization process and return an anonymized text.
    """

    def __init__(self, allow_list: Optional[List[str]] = None) -> None:
        """
        Initializes HebSafeHarbor
        :param allow_list: List of words that the user defines as being allowed to keep
        """
        self.identifier = PhiIdentifier()
        self.anonymizer = PhiAnonymizer()
        self.allow_list = allow_list

    def __call__(self, doc_list: List[Dict[str, str]], allow_list: Optional[List[str]] = None, extend_base_allow_list: bool = False) -> List[Doc]:
        """
        The main method, executes the PHI reduction process on the given text
        :param doc_list: List of dictionary where each dict represents a document.
                        Each dictionary should consist of "id" and "text" columns
        :param allow_list: List of words that the user defines as being allowed to keep
        :param extend_base_allow_list: If True, the allow_list will be added to the base allow list (for this instance only),
                        otherwise it will replace the base allow list
        :return: anonymized text
        """

        docs = [Doc(doc_dict) for doc_dict in doc_list]
        docs = self.identify(docs, allow_list=allow_list, extend_base_allow_list=extend_base_allow_list)
        docs = self.anonymize(docs)
        return docs

    def identify(self, docs: List[Doc], allow_list: Optional[List[str]] = None, extend_base_allow_list: bool = False) -> List[Doc]:
        """
        This method identifies the PHI entities in the input text
        :param docs: a list of Doc objects which contains the input text for anonymization
        :param allow_list: List of words that the user defines as being allowed to keep
        :param extend_base_allow_list: If True, the allow_list will be added to the base allow list (for this instance only),
                        otherwise it will replace the base allow list
        :return: a list of the updated Doc objects that contains the recognized PHI entities
        """

        if allow_list:
            if extend_base_allow_list:
                allow_list.extend(self.allow_list)
            # If allow_list is not None, and extend_base_allow_list is False, we use the given allow_list
        else:
            allow_list = self.allow_list
        return [self.identifier(doc, allow_list) for doc in docs]

    def anonymize(self, docs: List[Doc]) -> List[Doc]:
        """
        This method anonymizes the recognized PHI entities using different techniques
        :param doc: a list of Doc objects which contains the consolidated recognized PHI entities
        :return: a list of the updated Doc objects that contains the anonymized text
        """
        return [self.anonymizer(doc) for doc in docs]

    @staticmethod
    def create_result(doc: Doc) -> Dict[str, str]:
        """
        this function will get a document and create a result map.
        """

        items = []
        for item in doc.anonymized_text.items:
            item_result = {
                "startPosition": item.start,
                "endPosition": item.end,
                "entityType": item.entity_type,
                "text": doc.text[item.start:item.end],
                "mask": item.text,
                "operator": item.operator
            }
            items.append(item_result)

        result: Dict = {
            "id": doc.id,
            "text": doc.anonymized_text.text,
            "items": items
        }
        return result
