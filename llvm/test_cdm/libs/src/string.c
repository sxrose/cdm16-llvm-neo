#include "string.h"

void *memcpy(void *dest, const void *src, size_t count)
{
	char *tmp = (char *)dest;
	const char *s = (const  char *)src;
	while (count--)
		*tmp++ = *s++;
	return dest;
}

size_t strlen(const char *s)
{
	const char *sc;

	for (sc = s; *sc != '\0'; ++sc)
		/* nothing */;
	return sc - s;
}
