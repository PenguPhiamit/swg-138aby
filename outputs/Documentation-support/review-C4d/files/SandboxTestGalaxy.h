/*
				Copyright <SWGEmu>
		See file COPYING for copying conditions.*/

#ifndef SANDBOXTESTGALAXY_H_
#define SANDBOXTESTGALAXY_H_

#include "conf/ConfigManager.h"

/*
 * Sandbox: true only on a disposable test galaxy. test_galaxy.py points such a galaxy at its own database
 * named "*_test" (the live galaxy uses "swgemu"). Test-only helpers require this in addition to their own
 * config flag, so a flag copied into the live configuration by mistake still can't enable them there.
 */
inline bool isDisposableTestGalaxy() {
	return ConfigManager::instance()->getDBName().endsWith("_test");
}

#endif // SANDBOXTESTGALAXY_H_
