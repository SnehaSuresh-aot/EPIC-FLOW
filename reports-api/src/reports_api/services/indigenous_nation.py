# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service to manage IndigenousNation."""
from sqlalchemy import func
from reports_api.models import IndigenousNation


class IndigenousNationService:  # pylint: disable=too-few-public-methods
    """Service to manage indigenous nation related operations."""

    @classmethod
    def check_existence(cls, name, instance_id):
        """Checks if an indigenous nation exists with given name"""
        query = IndigenousNation.query.filter(
                    func.lower(IndigenousNation.name) == func.lower(name), IndigenousNation.is_deleted.is_(False)
        )
        if instance_id:
            query = query.filter(IndigenousNation.id != instance_id)
        if query.count() > 0:
            return {"exists": True}
        return {"exists": False}
