from django.contrib import admin

from ytdl.models import Video, Channel


class YtdlAdmin(admin.ModelAdmin):
    pass


admin.site.register(Video, YtdlAdmin)
admin.site.register(Channel, YtdlAdmin)
