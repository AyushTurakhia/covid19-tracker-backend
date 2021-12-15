from rest_framework import serializers
import re
date_regex = "^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$"

class StateDateSerializer(serializers.Serializer):
    state_code = serializers.CharField(allow_blank=False)
    start_date = serializers.CharField(allow_blank=False)
    end_date = serializers.CharField(allow_blank=False)
    def is_valid(self, raise_exception):
        isValid = super().is_valid(raise_exception=raise_exception)
        data = dict(self.data)
        if re.search(date_regex, data["start_date"]) or re.search(date_regex, data["end_date"]):
            return serializers.ValidationError("start date or end date not in proper format yyyy-mm-dd")
        elif re.search("^[A-Z]{2}$",data["state_code"]):
            return serializers.ValidationError("state code invalid")
        elif(data["start_date"]>=data["end_date"]):
            return serializers.ValidationError("start date should be less than end date")
        return isValid