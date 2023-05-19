from moto.core import BaseBackend, BackendDict, BaseModel
from moto.core.utils import iso_8601_datetime_with_milliseconds
from moto.moto_api._internal import mock_random
from datetime import datetime
from typing import Dict, List, Optional
from .exceptions import RepositoryDoesNotExistException, RepositoryNameExistsException


class CodeCommit(BaseModel):
    def __init__(
        self,
        account_id: str,
        region: str,
        repository_description: str,
        repository_name: str,
    ):
        current_date = iso_8601_datetime_with_milliseconds(datetime.utcnow())
        self.repository_metadata = {
            "repositoryName": repository_name,
            "cloneUrlSsh": f"ssh://git-codecommit.{region}.amazonaws.com/v1/repos/{repository_name}",
            "cloneUrlHttp": f"https://git-codecommit.{region}.amazonaws.com/v1/repos/{repository_name}",
            "creationDate": current_date,
            "lastModifiedDate": current_date,
            "repositoryDescription": repository_description,
            "repositoryId": str(mock_random.uuid4()),
            "Arn": f"arn:aws:codecommit:{region}:{account_id}:{repository_name}",
            "accountId": account_id,
        }


class CodeCommitBackend(BaseBackend):
    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.repositories: Dict[str, CodeCommit] = {}

    @staticmethod
    def default_vpc_endpoint_service(
        service_region: str, zones: List[str]
    ) -> List[Dict[str, str]]:
        """Default VPC endpoint service."""
        return BaseBackend.default_vpc_endpoint_service_factory(
            service_region, zones, "codecommit"
        )

    def create_repository(
        self, repository_name: str, repository_description: str
    ) -> Dict[str, str]:
        if repository := self.repositories.get(repository_name):
            raise RepositoryNameExistsException(repository_name)

        self.repositories[repository_name] = CodeCommit(
            self.account_id, self.region_name, repository_description, repository_name
        )

        return self.repositories[repository_name].repository_metadata

    def get_repository(self, repository_name: str) -> Dict[str, str]:
        if repository := self.repositories.get(repository_name):
            return repository.repository_metadata
        else:
            raise RepositoryDoesNotExistException(repository_name)

    def delete_repository(self, repository_name: str) -> Optional[str]:
        if repository := self.repositories.get(repository_name):
            self.repositories.pop(repository_name)
            return repository.repository_metadata.get("repositoryId")

        return None


codecommit_backends = BackendDict(CodeCommitBackend, "codecommit")
